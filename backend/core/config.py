from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    supabase_jwt_secret: str
    redis_url: str = "redis://localhost:6379"
    stripe_secret_key: str = ""
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    platform_fee_subscription: float = 0.10
    platform_fee_marketplace: float = 0.05
    cors_origins: str = "http://localhost:3000"
    amazon_affiliate_tag: str = ""
    flipkart_affiliate_id: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
