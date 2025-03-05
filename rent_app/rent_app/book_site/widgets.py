from django.forms import widgets
from django.utils.safestring import mark_safe


class StarRatingWidget(widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        html = '''
            <div class="star-rating">
                <input type="radio" name="{0}" value="1" {1} /> ★☆☆☆☆
                <input type="radio" name="{0}" value="2" {2} /> ★★☆☆☆
                <input type="radio" name="{0}" value="3" {3} /> ★★★☆☆
                <input type="radio" name="{0}" value="4" {4} /> ★★★★☆
                <input type="radio" name="{0}" value="5" {5} /> ★★★★★
            </div>
        '''.format(
            name,
            'checked="checked"' if value == 1 else '',
            'checked="checked"' if value == 2 else '',
            'checked="checked"' if value == 3 else '',
            'checked="checked"' if value == 4 else '',
            'checked="checked"' if value == 5 else '',
        )
        return mark_safe(html)
