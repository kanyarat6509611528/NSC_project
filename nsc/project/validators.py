from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)

class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        if user:
            if password == user.username:
                raise ValidationError(
                    _("รหัสผ่านต้องไม่เหมือนกับชื่อผู้ใช้ของคุณ"),
                    code='password_too_similar',
                )

class CustomMinimumLengthValidator(MinimumLengthValidator):
    def get_help_text(self):
        return _("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร")

class CustomCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return _("รหัสผ่านนี้เป็นรหัสผ่านที่ใช้บ่อย")

class CustomNumericPasswordValidator(NumericPasswordValidator):
    def get_help_text(self):
        return _("รหัสผ่านต้องมีตัวเลขอย่างน้อย 1 ตัว")
