from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.crud.profiles import (
    get_profiles_for_user,
    get_profile_by_id,
    update_profile,
    delete_profile,
    create_profile,
    get_weights_for_profile,
    delete_weight_entry,
    update_weight_entry,
    calculate_bmi,
    add_weight_to_profile
)

from app.crud.users import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    authenticate_user
)