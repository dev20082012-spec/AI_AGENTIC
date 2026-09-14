import os
import litellm

PROVIDER = "groq"
GROQ_MODEL_ID = "groq/qwen/qwen3.8-27b"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20251001-v1:0"
BEDROCK_REGION = "us-west-2"

litellm.num_retries = 6
litellm.retry_after = 3
litellm.drop_params = True

def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

_load_env_file()


def _check_env(var: str, hint: str):
    val = os.environ.get(var)
    if not val:
        raise SystemExit(
            f"\n[ERROR] Missing environment variable: {var}\n\n"
            f"  {hint}\n\n"
            f"  PowerShell:  $env:{var}='your_key_here'\n"
            f"  CMD:         set {var}=your_key_here\n"
        )
    return val


def get_model():
    if PROVIDER == "groq":
        try:
            from strands.models.litellm import LiteLLMModel
        except ImportError:
            raise SystemExit(
                "\n[ERROR] LiteLLM provider not installed.\n"
                "  Run: pip install 'strands-agents[litellm]' litellm\n"
            )

        _check_env(
            "GROQ_API_KEY",
            "Get a free key at https://console.groq.com -> API Keys\n"
            "  Then set it in your terminal before running orchestrator.py."
        )

        return LiteLLMModel(
            model_id=GROQ_MODEL_ID,
            params={
                "temperature": 0.3,
                "max_tokens": 800,
            },
        )

    elif PROVIDER == "bedrock":
        try:
            import boto3
            session = boto3.session.Session()
            creds = session.get_credentials()
            if creds is None or creds.resolve() is None:
                raise SystemExit(
                    "\n[ERROR] No AWS credentials found.\n\n"
                    "  Set them via:\n"
                    "    $env:AWS_ACCESS_KEY_ID='...'\n"
                    "    $env:AWS_SECRET_ACCESS_KEY='...'\n"
                    "    $env:AWS_DEFAULT_REGION='us-west-2'\n\n"
                    "  Also enable Bedrock model access for:\n"
                    f"    {BEDROCK_MODEL_ID}\n"
                    f"  in region '{BEDROCK_REGION}' via the AWS Bedrock console.\n"
                )
        except SystemExit:
            raise
        except Exception as e:
            raise SystemExit(f"\n[ERROR] AWS credential check failed: {e}\n") from e

        from strands.models import BedrockModel
        return BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=BEDROCK_REGION,
        )

    else:
        raise SystemExit(f"\n[ERROR] Unknown PROVIDER '{PROVIDER}' in model.py. Use 'groq' or 'bedrock'.\n")
