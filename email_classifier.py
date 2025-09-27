from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
import html as html_lib
from email import policy
from email.parser import BytesParser
from typing import Iterable, List, Optional, Tuple

from huggingface_hub import login as hf_login
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class ClassificationResult:
    file: Optional[str]
    chosen: Optional[str]
    labels: List[str]
    scores: List[Tuple[str, float]]
    subject: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    raw_model_output: Optional[str] = None
    error: Optional[str] = None


class GemmaEmailClassifier:
    """
    Minimal classifier that uses google/gemma-3-270m-it to classify .eml emails.

    Usage:
        clf = GemmaEmailClassifier(labels=["phishing", "spam", "benign"])  # optionally pass hf_token=
        res = clf.classify_eml_file("email/sample.eml")
        print(res.chosen, res.scores)
    """

    def __init__(
        self,
        model_id: str = "google/gemma-3-270m-it",
        labels: Optional[List[str]] = None,
        hf_token: Optional[str] = None,
        max_new_tokens: int = 128,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ) -> None:
        self.model_id = model_id
        self.labels = labels or ["phishing", "spam", "benign"]
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p

        # Login if token provided or present in env
        token = hf_token or os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if token:
            try:
                hf_login(token=token)
            except Exception:
                # Non-fatal; model may be public
                pass

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id)

    # -----------------------------
    # Public API
    # -----------------------------
    def classify_eml_file(self, path: str, labels: Optional[List[str]] = None) -> ClassificationResult:
        """Classify a single .eml file and return the result."""
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            msg = BytesParser(policy=policy.default).parsebytes(raw)
        except Exception as e:
            return ClassificationResult(
                file=os.path.basename(path),
                chosen=None,
                labels=labels or self.labels,
                scores=[],
                error=f"Failed to open/parse EML: {e}",
            )

        subject = msg.get("subject")
        sender = msg.get("from")
        recipient = msg.get("to")

        body_text = self._extract_text(msg)
        combined = ((subject or "") + "\n\n" + body_text).strip()
        if not combined:
            return ClassificationResult(
                file=os.path.basename(path),
                chosen=None,
                labels=labels or self.labels,
                scores=[],
                subject=subject,
                sender=sender,
                recipient=recipient,
                error="No textual content found",
            )

        chosen, scores, raw_out = self.classify_text(combined, labels=labels)
        return ClassificationResult(
            file=os.path.basename(path),
            chosen=chosen,
            labels=labels or self.labels,
            scores=scores,
            subject=subject,
            sender=sender,
            recipient=recipient,
            raw_model_output=raw_out,
        )

    def classify_directory(
        self, directory: str, limit: Optional[int] = None, offset: int = 0, labels: Optional[List[str]] = None
    ) -> List[ClassificationResult]:
        """Classify all .eml files in a directory (paged by limit/offset)."""
        if not os.path.isdir(directory):
            return [
                ClassificationResult(
                    file=None,
                    chosen=None,
                    labels=labels or self.labels,
                    scores=[],
                    error=f"Not a directory: {directory}",
                )
            ]

        files = [f for f in os.listdir(directory) if f.lower().endswith(".eml")]
        slice_files = files[offset : (offset + limit) if limit is not None else None]

        results: List[ClassificationResult] = []
        for name in slice_files:
            results.append(self.classify_eml_file(os.path.join(directory, name), labels=labels))
        return results

    def classify_text(self, text: str, labels: Optional[List[str]] = None) -> Tuple[Optional[str], List[Tuple[str, float]], str]:
        """
        Classify raw text by asking Gemma to choose exactly one label from the provided list.
        Returns: (chosen_label, scores, raw_output_text)
        """
        labs = labels or self.labels
        messages = self._build_messages(text=text, labels=labs)

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True,
        ).to(self.model.device)

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=(self.temperature > 0.0),
            temperature=self.temperature,
            top_p=self.top_p,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        # Only decode the generated continuation
        gen_only = output_ids[0][inputs["input_ids"].shape[-1] :]
        text_out = self.tokenizer.decode(gen_only, skip_special_tokens=True)

        chosen = self._parse_choice_label(text_out, labs)
        scores = self._heuristic_scores(text_out, labs) if chosen is None else [(chosen, 1.0)]
        return chosen, scores, text_out

    # -----------------------------
    # Helpers
    # -----------------------------
    @staticmethod
    def _extract_text(msg) -> str:
        """
        Extract human-readable text from an email.message.Message.
        - Prefer text/plain parts.
        - Fallback to text/html parts converted to plain text.
        - Handles base64 transfer-encoding automatically via email.policy.default.
        """
        plain_parts: List[str] = []
        html_parts: List[str] = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    try:
                        content = part.get_content()
                        if isinstance(content, str):
                            plain_parts.append(content)
                    except Exception:
                        pass
                elif ctype == "text/html":
                    try:
                        content = part.get_content()
                        if isinstance(content, str):
                            html_parts.append(content)
                    except Exception:
                        pass
        else:
            ctype = msg.get_content_type()
            try:
                content = msg.get_content()
            except Exception:
                content = None
            if isinstance(content, str):
                if ctype == "text/plain":
                    plain_parts.append(content)
                elif ctype == "text/html":
                    html_parts.append(content)

        if plain_parts:
            return "\n\n".join(plain_parts).strip()

        # Convert HTML to plain text as fallback
        html_texts = [GemmaEmailClassifier._html_to_text(h) for h in html_parts]
        return "\n\n".join([t for t in html_texts if t]).strip()

    @staticmethod
    def _html_to_text(html: str) -> str:
        """
        Minimal HTML to text conversion without external dependencies.
        - Removes script/style blocks.
        - Strips tags.
        - Unescapes HTML entities.
        """
        if not html:
            return ""
        # Remove script and style content
        cleaned = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
        cleaned = re.sub(r"<style[\s\S]*?</style>", " ", cleaned, flags=re.IGNORECASE)
        # Replace <br> and <p> with newlines to preserve some structure
        cleaned = re.sub(r"<(br|BR)\s*/?>", "\n", cleaned)
        cleaned = re.sub(r"</p>", "\n\n", cleaned, flags=re.IGNORECASE)
        # Strip remaining tags
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        # Unescape entities
        cleaned = html_lib.unescape(cleaned)
        # Collapse whitespace
        cleaned = re.sub(r"[\t\r\f]+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip()

    @staticmethod
    def _build_messages(text: str, labels: List[str]) -> list[dict]:
        label_list = ", ".join(labels)
        system_prompt = (
            "You are an email security classifier. Given an email's subject and body, "
            "select exactly one label from the provided options. "
            "Respond ONLY with a compact JSON object like: {\"label\": \"<one_of_labels>\"}."
        )
        user_prompt = (
            f"Labels: [{label_list}]\n\n"
            f"Email:\n{text.strip()}\n\n"
            "Return JSON only."
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def _parse_choice_label(output_text: str, labels: List[str]) -> Optional[str]:
        # Try to extract JSON {"label": "..."}
        try:
            m = re.search(r"\{.*?\}", output_text, flags=re.DOTALL)
            if m:
                obj = json.loads(m.group(0))
                if isinstance(obj, dict) and "label" in obj:
                    label = str(obj["label"]).strip().lower()
                    # Normalize to one of provided labels
                    low_map = {l.lower(): l for l in labels}
                    if label in low_map:
                        return low_map[label]
        except Exception:
            pass
        
        # Fallback: look for labels directly in the text
        output_lower = output_text.lower()
        for label in labels:
            if label.lower() in output_lower:
                return label
        
        # Enhanced fallback: look for common variations
        if any(word in output_lower for word in ["phish", "fraud", "scam", "malicious"]):
            return "phishing"
        elif any(word in output_lower for word in ["spam", "junk", "marketing", "promotional"]):
            return "spam"
        elif any(word in output_lower for word in ["benign", "legitimate", "safe", "normal", "clean"]):
            return "benign"
        
        # If we still can't determine, return the first label as default
        return labels[0] if labels else None

    @staticmethod
    def _heuristic_scores(output_text: str, labels: List[str]) -> List[Tuple[str, float]]:
        # Fallback: count occurrences of each label in the output
        out = output_text.lower()
        scored = [(l, float(out.count(l.lower()))) for l in labels]
        scored.sort(key=lambda x: -x[1])
        return scored
