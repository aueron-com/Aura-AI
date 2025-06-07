# --- core/prompts.py ---
# Advanced AI prompt engineering system for interview coaching

from core.config import settings
from typing import Dict, List, Optional

def build_candidate_profile(context: dict) -> str:
    """Build a comprehensive candidate profile section for prompts."""
    if not settings.PERSONALIZE_ANSWERS:
        return ""
    
    profile_parts = []
    
    if context.get('name'):
        profile_parts.append(f"Candidate Name: {context['name']}")
    
    if context.get('company'):
        profile_parts.append(f"Target Company: {context['company']}")
    
    if context.get('role'):
        profile_parts.append(f"Target Role: {context['role']}")
    
    if context.get('focus') and len(context['focus']) > 0:
        focus_areas = ', '.join(context['focus'])
        profile_parts.append(f"Interview Focus Areas: {focus_areas}")
    
    if context.get('resume'):
        # Truncate resume for prompt efficiency
        resume_preview = context['resume'][:800] + "..." if len(context['resume']) > 800 else context['resume']
        profile_parts.append(f"Resume/Background:\n{resume_preview}")
    
    if context.get('objectives'):
        # Truncate job description for prompt efficiency
        job_preview = context['objectives'][:600] + "..." if len(context['objectives']) > 600 else context['objectives']
        profile_parts.append(f"Job Description/Requirements:\n{job_preview}")
    
    return "\n".join(profile_parts) + "\n" if profile_parts else ""

def build_conversation_context(conversation_history: List[Dict]) -> str:
    """Build conversation context from recent exchanges."""
    if not settings.INCLUDE_CONVERSATION_HISTORY or not conversation_history:
        return ""
    
    context_parts = ["Recent conversation context:"]
    
    # Take the last few exchanges
    recent_history = conversation_history[-settings.MAX_CONVERSATION_HISTORY:]
    
    for exchange in recent_history:
        if exchange.get('interviewer_question'):
            context_parts.append(f"INTERVIEWER: {exchange['interviewer_question']}")
        if exchange.get('candidate_response'):
            context_parts.append(f"CANDIDATE: {exchange['candidate_response']}")
    
    if len(context_parts) > 1:  # More than just the header
        return "\n".join(context_parts) + "\n"
    return ""

def get_interview_answer_prompt(question: str, context: dict, conversation_history: List[Dict] = None) -> str:
    """
    Generates a comprehensive prompt for full interview answers.
    
    Args:
        question: The question asked by the interviewer
        context: Candidate profile and job information
        conversation_history: Recent conversation exchanges
    
    Returns:
        A detailed prompt for generating complete interview answers
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # Build the comprehensive prompt
    prompt_parts = []
    
    # System role
    prompt_parts.append("""You are an expert interview coach providing real-time assistance during a live job interview.
Your goal is to help the candidate give the best possible answer to the interviewer's question.""")
    
    # Candidate profile (if personalization is enabled)
    candidate_profile = build_candidate_profile(context)
    if candidate_profile:
        prompt_parts.append("CANDIDATE PROFILE:")
        prompt_parts.append(candidate_profile)
    
    # Conversation context (if available and enabled)
    conversation_context = build_conversation_context(conversation_history)
    if conversation_context:
        prompt_parts.append(conversation_context)
    
    # Current question
    prompt_parts.append(f"CURRENT INTERVIEWER QUESTION: \"{question}\"")
    
    # Get question type for specialized instructions
    question_type = detect_question_type(question)
    
    # Instructions for response based on question type
    if settings.GENERATE_FULL_ANSWERS:
        if question_type == 'coding':
            prompt_parts.append(f"""
INSTRUCTIONS FOR CODING QUESTION:
Provide a complete, comprehensive coding answer. The response should include:

1. **Language Recognition**: Pay CLOSE attention to the programming language mentioned in the question
2. **Multiple Approaches**: Provide at least 2 different solutions (e.g., iterative vs recursive, brute force vs optimized)
3. **Complete Code**: Write fully functional, syntactically correct code in the EXACT language requested
4. **Complexity Analysis**: Include time and space complexity for each approach
5. **Explanation**: Brief explanation of how the algorithm works
6. **Best Practices**: Use clean, readable code with proper variable names

CRITICAL: If the question specifies a programming language (e.g., "JavaScript", "Python", "Java"), 
use ONLY that language. Do not provide code in a different language.

ANSWER FORMAT:
Structure your response as:
- Brief explanation of the problem
- Approach 1: [Method name] with code and complexity
- Approach 2: [Method name] with code and complexity  
- Recommendation of which approach to use and why

COMPLETE CODING ANSWER:""")
        
        elif question_type == 'system_design':
            prompt_parts.append("""
INSTRUCTIONS FOR SYSTEM DESIGN QUESTION:
Provide a comprehensive system design answer that includes:

1. **Requirements Clarification**: What are the key functional and non-functional requirements?
2. **High-Level Architecture**: Main components and their interactions
3. **Database Design**: What type of database(s) and why
4. **Scalability Considerations**: How to handle growth
5. **Technology Choices**: Specific technologies and justification
6. **Trade-offs**: Discuss pros/cons of design decisions

COMPLETE SYSTEM DESIGN ANSWER:""")
        
        elif question_type == 'technical':
            prompt_parts.append("""
INSTRUCTIONS FOR TECHNICAL QUESTION:
Provide a detailed technical answer that includes:

1. **Clear Definition**: Explain the concept clearly
2. **Use Cases**: When and why it's used
3. **Advantages/Disadvantages**: Pros and cons
4. **Real-world Examples**: Practical applications
5. **Best Practices**: How to implement it well
6. **Related Technologies**: What it works with

COMPLETE TECHNICAL ANSWER:""")
        
        elif question_type == 'behavioral':
            prompt_parts.append("""
INSTRUCTIONS FOR BEHAVIORAL QUESTION:
Provide a complete behavioral answer using the STAR method:

1. **Situation**: Set the context
2. **Task**: Explain what needed to be done
3. **Action**: Describe what you specifically did
4. **Result**: Share the outcome and what you learned

Use the candidate's background and experience from their resume.

COMPLETE BEHAVIORAL ANSWER:""")
        
        else:  # general questions
            prompt_parts.append("""
INSTRUCTIONS:
Provide a complete, professional answer that the candidate can use verbatim. The answer should:

1. DIRECTLY address the question asked
2. Be tailored to the candidate's background and the target role
3. Demonstrate relevant skills and experience from their resume
4. Use specific examples when appropriate
5. Be conversational and natural (avoid being overly formal)
6. Be concise but comprehensive

ANSWER FORMAT:
Provide ONLY the answer the candidate should give. Do NOT include phrases like "You should say" or "Suggest saying". 
Write as if you ARE the candidate speaking directly to the interviewer.

COMPLETE, DETAILED, AND PROFESSIONAL ANSWER:""")
    else:
        prompt_parts.append("""
INSTRUCTIONS:
Provide a brief suggestion or key talking points for answering this question.
Keep it concise and actionable.

SUGGESTION:""")
    
    return "\n".join(prompt_parts)

def get_quick_response_prompt(question: str, context: dict = None) -> str:
    """
    Generates a quick, simple prompt for basic questions with essential context.
    Now includes resume highlights to ensure AI knows about candidate's actual projects.
    """
    if not context:
        return f"""Interview question: "{question}"

Give a brief, professional answer.

Answer:"""
    
    # Essential candidate info
    name = context.get('name', '')
    role = context.get('role', '')
    company = context.get('company', '')
    resume = context.get('resume', '')
    
    # Build basic profile
    profile_parts = []
    if name and role and company:
        profile_parts.append(f"You are {name}, applying for {role} at {company}.")
    
    # Include key resume highlights (especially projects)
    if resume:
        # Extract project mentions and key skills for context
        resume_preview = resume[:1000] + "..." if len(resume) > 1000 else resume
        profile_parts.append(f"Key background: {resume_preview}")
    
    profile_context = "\n".join(profile_parts) if profile_parts else ""
    
    return f"""Interview question: "{question}"

CANDIDATE PROFILE:
{profile_context}

Give a professional answer that draws from your actual background and projects. Be specific and authentic.

Answer:"""

def detect_question_type(question: str) -> str:
    """
    Detects the type of interview question for specialized handling.
    """
    question_lower = question.lower()
    
    # Coding question indicators
    coding_indicators = [
        'write', 'code', 'implement', 'algorithm', 'function', 'method', 'program',
        'javascript', 'python', 'java', 'c++', 'react', 'node', 'html', 'css',
        'array', 'string', 'linked list', 'tree', 'graph', 'sort', 'search',
        'leetcode', 'hackerrank', 'binary search', 'merge sort', 'fibonacci',
        'reverse', 'palindrome', 'duplicate', 'largest', 'smallest', 'sum',
        'find the', 'return the', 'given an array', 'given a string', 'hashmap'
    ]
    
    # System design indicators
    system_design_indicators = [
        'design', 'architecture', 'system', 'scale', 'database', 'api',
        'microservices', 'load balancer', 'cache', 'redis', 'mongodb',
        'scalability', 'high availability', 'distributed', 'messaging'
    ]
    
    # Technical knowledge indicators
    technical_indicators = [
        'what is', 'difference between', 'explain', 'how does', 'when to use',
        'pros and cons', 'advantages', 'disadvantages', 'framework', 'library',
        'protocol', 'rest', 'graphql', 'oauth', 'jwt', 'cors', 'https'
    ]
    
    # Behavioral/experience indicators
    behavioral_indicators = [
        'tell me about', 'describe', 'walk me through', 'give me an example',
        'how would you', 'what would you do', 'how do you handle', 'what is your experience',
        'why do you want', 'why should we hire', 'what are your', 'where do you see yourself',
        'introduction', 'introduce yourself', 'about yourself', 'background',
        'challenge', 'conflict', 'mistake', 'failure', 'success'
    ]
    
    if any(indicator in question_lower for indicator in coding_indicators):
        return 'coding'
    elif any(indicator in question_lower for indicator in system_design_indicators):
        return 'system_design'
    elif any(indicator in question_lower for indicator in technical_indicators):
        return 'technical'
    elif any(indicator in question_lower for indicator in behavioral_indicators):
        return 'behavioral'
    else:
        return 'general'

def is_complex_question(question: str) -> bool:
    """
    Determines if a question requires the full context treatment or can use a quick response.
    """
    question_type = detect_question_type(question)
    # All types except general are considered complex
    return question_type != 'general'