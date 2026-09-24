import os
import streamlit as st
from groq import Groq

# ---------------------------------------------------------
# App configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✍️",
    layout="wide",
)

DEFAULT_MODEL = "openai/gpt-oss-20b"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_groq_client():
    """Create a Groq client from the GROQ_API_KEY environment variable."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


def build_prompt(content_type, platform, topic, audience, tone, extra_instructions):
    """Build a platform-aware prompt for the Groq model."""

    platform_guidance = {
        "Instagram": (
            "Create visually engaging, concise content. Make the first line "
            "attention-grabbing and use natural Instagram-style formatting."
        ),
        "Facebook": (
            "Create conversational, shareable content with a strong hook, "
            "readable paragraphs, and a natural engagement prompt."
        ),
        "TikTok": (
            "Make the content punchy, curiosity-driven, and suitable for a "
            "short-form video caption/description."
        ),
        "LinkedIn": (
            "Use a professional, useful, insight-driven style with short "
            "paragraphs and a thoughtful call to action."
        ),
        "X (Twitter)": (
            "Keep the main post concise and punchy. Avoid unnecessary filler "
            "and use only a small number of highly relevant hashtags."
        ),
        "YouTube": (
            "Create engaging content suitable for a YouTube community post "
            "or video description, encouraging viewers to interact."
        ),
    }

    content_guidance = {
        "Educational": "Teach something useful in a simple and practical way.",
        "Promotional": "Highlight benefits and value without sounding excessively salesy.",
        "Inspirational": "Create an uplifting and motivating message.",
        "Entertainment": "Prioritize curiosity, personality, fun, and shareability.",
        "Storytelling": "Use a clear hook, narrative progression, and memorable ending.",
        "Informational": "Present useful information clearly and accurately.",
        "Tips & Tricks": "Give practical, actionable tips the audience can use.",
        "Question / Discussion": "Encourage meaningful discussion and comments.",
    }

    extra = extra_instructions.strip() if extra_instructions else "None"

    return f"""
You are a professional social-media content strategist and copywriter.

Create an original, high-quality social-media content package.

INPUTS
Content Type: {content_type}
Platform: {platform}
Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Additional Instructions: {extra}

PLATFORM GUIDANCE
{platform_guidance.get(platform, "Optimize naturally for the selected platform.")}

CONTENT-TYPE GUIDANCE
{content_guidance.get(content_type, "Follow the selected content type.")}

QUALITY RULES
- Match the requested audience and tone.
- Start with a strong hook.
- Make the writing natural and human-sounding.
- Avoid generic filler and repetitive phrases.
- Do not invent statistics, studies, quotes, or specific factual claims.
- Include a useful call to action where appropriate.
- Use relevant hashtags only.
- Do not use excessive hashtags.
- Keep the content platform-appropriate.

Return ONLY the following structure:

## POST
Write the complete post here.

## CAPTION
Write a polished caption here.

## HASHTAGS
Write relevant hashtags separated by spaces.

## CTA
Write a short call to action here.
"""


def generate_content(
    content_type,
    platform,
    topic,
    audience,
    tone,
    extra_instructions,
    model,
):
    """Generate content using Groq."""

    if not topic.strip():
        raise ValueError("Please enter a topic.")

    if not audience.strip():
        raise ValueError("Please enter a target audience.")

    client = get_groq_client()

    if client is None:
        raise ValueError(
            "GROQ_API_KEY is missing. Add your Groq API key to the environment "
            "or Streamlit secrets before generating content."
        )

    prompt = build_prompt(
        content_type,
        platform,
        topic,
        audience,
        tone,
        extra_instructions,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
               {"role": "system", "content": "..."},
               {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=1800,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("✍️ AI Content Assistant")
st.caption(
    "Generate platform-ready posts, captions, hashtags, and calls to action "
    "with Groq."
)

with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox(
        "Groq Model",
     options=[
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]
        
        index=0,
        help="Use the available Groq model you have access to.",
    )

    st.divider()

    st.markdown(
        """
        **API Key Setup**

        Set your Groq API key as:

        `GROQ_API_KEY`

        For Streamlit Cloud, add it under:

        **App Settings → Secrets**
        """
    )

left, right = st.columns(2)

with left:
    st.subheader("🎯 Content Inputs")

    content_type = st.selectbox(
        "Content Type",
        [
            "Educational",
            "Promotional",
            "Inspirational",
            "Entertainment",
            "Storytelling",
            "Informational",
            "Tips & Tricks",
            "Question / Discussion",
        ],
    )

    platform = st.selectbox(
        "Platform",
        [
            "Instagram",
            "Facebook",
            "TikTok",
            "LinkedIn",
            "X (Twitter)",
            "YouTube",
        ],
    )

    topic = st.text_area(
        "Topic",
        placeholder="Example: 5 AI tools that can save creators hours every week",
        height=120,
    )

    audience = st.text_input(
        "Target Audience",
        placeholder="Example: Beginner content creators aged 18–35",
    )

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Friendly",
            "Casual",
            "Inspirational",
            "Funny",
            "Educational",
            "Persuasive",
            "Bold",
            "Conversational",
        ],
    )

    extra_instructions = st.text_area(
        "Additional Instructions (Optional)",
        placeholder="Example: Keep it under 150 words and end with a question.",
        height=100,
    )

    generate = st.button(
        "🚀 Generate Content",
        type="primary",
        use_container_width=True,
    )

with right:
    st.subheader("✨ Generated Content")

    if generate:
        with st.spinner("Creating your content..."):
            try:
                result = generate_content(
                    content_type=content_type,
                    platform=platform,
                    topic=topic,
                    audience=audience,
                    tone=tone,
                    extra_instructions=extra_instructions,
                    model=model,
                )

                st.success("Content generated successfully!")
                st.markdown(result)

                st.download_button(
                    label="📥 Download as TXT",
                    data=result,
                    file_name="generated_content.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Could not generate content: {e}")

    else:
        st.info(
            "Fill in the content details on the left and click "
            "**Generate Content**."
        )

st.divider()

st.caption(
    "Powered by Streamlit + Groq. Never expose your GROQ_API_KEY in public source code."
)
