"""Keep the structured request and raw reply for bounded repair advice."""
from app.llm.gemini_client import GeminiError
from app.llm.repair_advisor import advise_repair


def traced_repair_advice(request, warning_type, candidates):
    transcript = []

    def capture(warning, options):
        entry = {'warning': warning, 'options': options}
        transcript.append(entry)
        try:
            text, usage = request(warning, options)
        except GeminiError as error:
            entry['error'] = str(error)
            raise
        entry['response'] = text
        return text, usage

    advice = advise_repair(capture, warning_type, candidates)
    advice['transcript'] = transcript
    return advice
