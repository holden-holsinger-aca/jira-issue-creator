#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate JIRA ticket details (description and acceptance criteria) via LLM.

Uses local Ollama model to enhance ticket summaries with full descriptions
and acceptance criteria based on a template.
"""

import os
import sys
import time
import threading
from typing import List, Dict, Any

try:
    import ollama
except ImportError:
    print("ERROR: Missing dependency. Install with: pip install ollama", file=sys.stderr)
    sys.exit(1)

TEMPLATE_FILE = "template.txt"
PLACEHOLDER = "[TICKET DESCRIPTION GOES HERE]"

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "phi3")
TEMPERATURE = 0.2
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 3


def read_file(path: str) -> str:
    """Read file contents."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_prompt(template: str, ticket_summary: str) -> str:
    """Replace placeholder in template with the ticket summary."""
    if PLACEHOLDER not in template:
        raise ValueError(
            f"Template must contain the exact placeholder: {PLACEHOLDER}"
        )
    return template.replace(PLACEHOLDER, ticket_summary.strip())


class ProgressIndicator:
    """Animated progress indicator with cycling dots."""
    
    def __init__(self, message: str):
        self.message = message
        self.running = False
        self.thread = None
    
    def _animate(self):
        """Display animated dots while running."""
        dot_count = 0
        while self.running:
            dots = "." * (dot_count + 1)
            spaces = " " * (3 - dot_count)
            sys.stdout.write(f"\r{self.message}{dots}{spaces}")
            sys.stdout.flush()
            dot_count = (dot_count + 1) % 4
            time.sleep(0.5)
    
    def start(self):
        """Start the animation."""
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self, clear: bool = True):
        """Stop the animation."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if clear:
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()


def call_ollama(prompt_text: str, model: str = DEFAULT_MODEL, progress_msg: str = None) -> str:
    """Call local Ollama LLM with retry logic and optional progress indicator."""
    indicator = None
    if progress_msg:
        indicator = ProgressIndicator(progress_msg)
        indicator.start()
    
    try:
        last_err = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = ollama.chat(
                    model=model,
                    options={"temperature": TEMPERATURE},
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert product manager crafting precise JIRA tickets. "
                                "Follow the user's template exactly."
                            ),
                        },
                        {"role": "user", "content": prompt_text},
                    ],
                )
                content = response["message"]["content"]
                if not content or not content.strip():
                    raise ValueError("Empty response content from the model.")
                return content.strip()
            except Exception as e:
                last_err = e
                if attempt < MAX_RETRIES:
                    sleep_s = RETRY_BACKOFF_SECONDS * attempt
                    if indicator:
                        indicator.stop(clear=True)
                    print(
                        f"[warn] Ollama call failed (attempt {attempt}/{MAX_RETRIES}): {e}. "
                        f"Retrying in {sleep_s}s...",
                        file=sys.stderr,
                    )
                    time.sleep(sleep_s)
                    if indicator:
                        indicator.start()
                else:
                    if indicator:
                        indicator.stop(clear=True)
                    print(
                        f"[error] Ollama call failed after {MAX_RETRIES} attempts: {e}",
                        file=sys.stderr,
                    )
                    raise

        raise RuntimeError(f"Ollama call failed: {last_err}")
    finally:
        if indicator:
            indicator.stop(clear=True)


def parse_llm_response(response: str) -> Dict[str, str]:
    """
    Parse LLM response to extract description and acceptance criteria.
    
    Expected format:
    1. Title / Summary
    2. User Story (description)
    3. Acceptance Criteria
    
    Returns dict with 'description' and 'acceptance_criteria' keys.
    """
    lines = response.split('\n')
    description = ""
    acceptance_criteria = ""
    
    # Find User Story section
    user_story_start = -1
    acceptance_start = -1
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if 'user story' in line_lower and user_story_start == -1:
            user_story_start = i
        elif 'acceptance criteria' in line_lower and acceptance_start == -1:
            acceptance_start = i
    
    # Extract description (User Story section)
    if user_story_start != -1:
        if acceptance_start != -1:
            description_lines = lines[user_story_start + 1:acceptance_start]
        else:
            description_lines = lines[user_story_start + 1:]
        description = '\n'.join(line.strip() for line in description_lines if line.strip())
    
    # Extract acceptance criteria
    if acceptance_start != -1:
        criteria_lines = lines[acceptance_start + 1:]
        acceptance_criteria = '\n'.join(line.strip() for line in criteria_lines if line.strip())
    
    # Fallback: if parsing fails, use entire response
    if not description and not acceptance_criteria:
        description = response
        acceptance_criteria = "See description for details."
    
    return {
        "description": description.strip(),
        "acceptance_criteria": acceptance_criteria.strip()
    }


def generate_ticket_details(summaries: List[str], template_path: str = TEMPLATE_FILE) -> List[Dict[str, str]]:
    """
    Generate ticket details (description and acceptance criteria) for a list of summaries.
    
    Args:
        summaries: List of ticket summary strings
        template_path: Path to the template file (default: template.txt)
    
    Returns:
        List of dicts, each containing:
        - 'summary': Original summary
        - 'description': Generated description/user story
        - 'acceptance_criteria': Generated acceptance criteria
        - 'full_response': Complete LLM response (for debugging)
    """
    try:
        template = read_file(template_path)
    except Exception as e:
        print(f"ERROR: Cannot read template: {e}", file=sys.stderr)
        raise
    
    if not summaries:
        print("WARNING: No summaries provided to generate_ticket_details.", file=sys.stderr)
        return []
    
    print(f"\n{'='*60}")
    print(f"Generating ticket details for {len(summaries)} ticket(s) using {DEFAULT_MODEL}")
    print(f"{'='*60}")
    
    results = []
    total_start_time = time.time()
    
    for idx, summary in enumerate(summaries, start=1):
        print(f"\n[{idx}/{len(summaries)}] Processing: {summary[:60]}...")
        
        ticket_start_time = time.time()
        try:
            prompt = render_prompt(template, summary)
            progress_msg = f"Generating ticket {idx}/{len(summaries)}"
            llm_response = call_ollama(prompt, progress_msg=progress_msg)
            parsed = parse_llm_response(llm_response)
            
            result = {
                "summary": summary,
                "description": parsed["description"],
                "acceptance_criteria": parsed["acceptance_criteria"],
                "full_response": llm_response
            }
            results.append(result)
            
            ticket_runtime = time.time() - ticket_start_time
            print(f"✅ Generated details (runtime: {ticket_runtime:.2f}s)")
            
        except Exception as e:
            ticket_runtime = time.time() - ticket_start_time
            print(f"❌ Failed to generate details: {e} (runtime: {ticket_runtime:.2f}s)", file=sys.stderr)
            # Add placeholder data to maintain list alignment
            results.append({
                "summary": summary,
                "description": "Failed to generate description",
                "acceptance_criteria": "Failed to generate acceptance criteria",
                "full_response": str(e)
            })
    
    total_runtime = time.time() - total_start_time
    print(f"\n{'='*60}")
    print(f"Completed {len(results)}/{len(summaries)} tickets")
    print(f"Total runtime: {total_runtime:.2f}s")
    print(f"{'='*60}\n")
    
    return results


# For backward compatibility / standalone testing
def main():
    """
    Standalone mode: reads from tickets.txt and writes to output files.
    This maintains backward compatibility with the original workflow.
    """
    TICKETS_FILE = "documentation/tickets.txt"
    OUTPUT_FOLDER = "documentation/output"
    OUTPUT_BASENAME = "ticket"
    
    try:
        tickets_raw = read_file(TICKETS_FILE)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse semicolon-separated tickets
    normalized = tickets_raw.replace("\n", " ").replace("\r", " ")
    parts = [p.strip() for p in normalized.split(";")]
    summaries = [p for p in parts if p]
    
    if not summaries:
        print(f"ERROR: No ticket descriptions found in {TICKETS_FILE}.", file=sys.stderr)
        sys.exit(1)
    
    # Generate details
    results = generate_ticket_details(summaries)
    
    # Write to files
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    for idx, result in enumerate(results, start=1):
        out_path = os.path.join(OUTPUT_FOLDER, f"{OUTPUT_BASENAME}{idx}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result["full_response"])
        print(f"Wrote {out_path}")
    
    print(f"\nDone. {len(results)} ticket(s) generated in {OUTPUT_FOLDER}/")


if __name__ == "__main__":
    main()
