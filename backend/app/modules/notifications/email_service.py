"""Email notification service — placeholder for SMTP integration."""
import logging

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> bool:
    """Placeholder: log email instead of sending. Configure SMTP in production."""
    logger.info("EMAIL [%s] Subject: %s | Body: %s", to, subject, body)
    return True


async def send_tournament_invite(email: str, tournament_name: str) -> bool:
    """Gửi email mời tham gia giải đấu."""
    return await send_email(
        email,
        f"Mời tham gia giải: {tournament_name}",
        f"Bạn được mời tham gia giải đấu {tournament_name}",
    )


async def send_match_result(email: str, result: str) -> bool:
    """Gửi email thông báo kết quả ván đấu."""
    return await send_email(email, "Kết quả ván đấu", f"Kết quả: {result}")


async def send_password_reset(email: str, reset_link: str) -> bool:
    """Gửi email đặt lại mật khẩu."""
    return await send_email(
        email,
        "Đặt lại mật khẩu VCC Platform",
        f"Nhấn vào link để đặt lại mật khẩu: {reset_link}",
    )
