<form method="post" action="">
    {{ formset.management_form }}
    {% for form in formset %}
        {{ form.id }}
        <ul>
            <li>{{ form.title }}</li>
            <li>{{ form.content }}</li>
        </ul>
    {% endfor %}
</form>