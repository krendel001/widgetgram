from aiogram.types import TelegramObject


class AreaPosition(TelegramObject):
    x_percentage: float
    y_percentage: float
    width_percentage: float
    height_percentage: float
    rotation_angle: float
    corner_radius_percentage: float
