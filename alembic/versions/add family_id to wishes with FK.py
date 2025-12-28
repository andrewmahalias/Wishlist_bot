"""add family_id to wishes with FK"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'aa650b072e3f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Додаємо колонку nullable
    op.add_column('wishes', sa.Column('family_id', sa.Integer(), nullable=True))

    # 2. За потреби, встановлюємо дефолтне значення для існуючих рядків
    # Тут можна підставити id існуючої сім'ї або створити окрему "default" сім'ю
    op.execute("UPDATE wishes SET family_id = 1 WHERE family_id IS NULL")

    # 3. Робимо колонку NOT NULL
    op.alter_column('wishes', 'family_id', nullable=False)

    # 4. Додаємо зовнішній ключ на таблицю families
    op.create_foreign_key(
        'fk_wishes_family',
        'wishes',
        'families',
        ['family_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # При відкаті видаляємо FK і колонку
    op.drop_constraint('fk_wishes_family', 'wishes', type_='foreignkey')
    op.drop_column('wishes', 'family_id')
