from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid

class Base(DeclarativeBase):
    pass


class UserRole(Enum):
    """Enumeration of user roles within the application."""
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class User(Base):
    """
    Represents a user within the application, corresponding to the 'users' table.
    Uses SQLAlchemy ORM for efficient mapping of attributes to database columns.
    """
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}  # ✅ Prevents duplicate table definitions
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = Column(String(100), nullable=True)
    last_name: Mapped[str] = Column(String(100), nullable=True)
    bio: Mapped[str] = Column(String(500), nullable=True)
    profile_picture_url: Mapped[str] = Column(String(255), nullable=True)
    linkedin_profile_url: Mapped[str] = Column(String(255), nullable=True)
    github_profile_url: Mapped[str] = Column(String(255), nullable=True)
    role: Mapped[str] = Column(Enum(UserRole, name='UserRole', create_constraint=False), default=UserRole.ANONYMOUS, nullable=False)
    is_professional: Mapped[bool] = Column(Boolean, default=False)
    professional_status_updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[DateTime] = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = Column(Integer, default=0)
    is_locked: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    verification_token: Mapped[str] = Column(String, nullable=True)
    email_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    hashed_password: Mapped[str] = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        """Provides a readable representation of a user object."""
        return f"<User {self.nickname}, Role: {self.role.name}>"

    def lock_account(self):
        """Locks the user account."""
        self.is_locked = True

    def unlock_account(self):
        """Unlocks the user account."""
        self.is_locked = False

    def verify_email(self):
        """Marks the user's email as verified."""
        self.email_verified = True

    def has_role(self, role_name: UserRole) -> bool:
        """Checks if the user has a specified role."""
        return self.role == role_name

    def update_professional_status(self, status: bool):
        """Updates the professional status and logs the update time."""
        self.is_professional = status
        self.professional_status_updated_at = func.now()