#!/usr/bin/env python3
"""
Seed default tracking fields for each department.
"""

from app import create_app, db
from app.models import Department, TrackingField
from default_tracking_fields import get_default_tracking_fields_by_key, match_department_key


def seed_defaults():
    app = create_app()
    defaults = get_default_tracking_fields_by_key()

    with app.app_context():
        departments = Department.query.all()
        if not departments:
            print("No departments found. Run init_db.py first.")
            return

        created = 0
        skipped = 0

        for dept in departments:
            key = match_department_key(dept.name)
            if not key:
                skipped += 1
                continue

            existing = TrackingField.query.filter_by(department_id=dept.id).count()
            if existing > 0:
                skipped += 1
                continue

            fields = defaults.get(key, [])
            for order_index, field_def in enumerate(fields, start=1):
                field = TrackingField(
                    department_id=dept.id,
                    field_name=field_def["name"],
                    field_label=field_def["label"],
                    field_type=field_def["type"],
                    is_required=False,
                    order=order_index,
                )
                if field_def.get("choices"):
                    field.set_choices(field_def["choices"])

                db.session.add(field)
                created += 1

        db.session.commit()
        print(f"Default fields added: {created}")
        print(f"Departments skipped (already configured or no match): {skipped}")


if __name__ == "__main__":
    seed_defaults()
