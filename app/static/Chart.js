{% extends "base.html" %}
{% block content %}
<h2>Welcome {{ user.name }} ({{ user.department }})</h2>
<p>Daily: {{ summary.daily }}, Weekly: {{ summary.weekly }}, Monthly: {{ summary.monthly }}</p>

<canvas id="productivityChart" width="400" height="200"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('productivityChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Daily','Weekly','Monthly'],
        datasets:[{
            label: 'Productivity Entries',
            data: [{{ summary.daily }}, {{ summary.weekly }}, {{ summary.monthly }}],
            backgroundColor: ['#36a2eb','#ffcd56','#ff6384']
        }]
    }
});
</script>
{% endblock %}
