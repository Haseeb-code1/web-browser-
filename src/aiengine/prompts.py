class AIPrompts:
    """Centralized prompts for Phi-3 Mini local AI."""
    
    SUMMARIZE_PAGE = (
        "You are an AI browser assistant. Briefly summarize the following webpage content:\n"
        "Title: {title}\n"
        "Content snippet: {content}\n"
    )
    
    EXPLAIN_CODE = (
        "Explain the following code snippet found on this webpage:\n"
        "```\n{code_snippet}\n```"
    )
