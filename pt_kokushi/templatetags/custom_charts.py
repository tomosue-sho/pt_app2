from django import template

register = template.Library()

@register.filter(name='divide_by_60')
def divide_by_60(value):
    try:
        # 値を60で割り、小数点以下2桁で丸める
        return round(value / 60, 2)
    except (ValueError, TypeError):
        return value  # 変換できない場合は元の値をそのまま返す
