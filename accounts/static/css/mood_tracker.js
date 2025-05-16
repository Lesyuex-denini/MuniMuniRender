document.addEventListener('DOMContentLoaded', function() {
    const calendar = document.getElementById('calendar');
    const selectedMood = { mood: null };
    const moodData = {}; // store mood per day (e.g., 1: 'happy')

    function generateCalendar() {
        calendar.innerHTML = '';
        for (let day = 1; day <= 30; day++) {
            const dayDiv = document.createElement('div');
            dayDiv.classList.add('day');
            dayDiv.innerText = day;
            dayDiv.dataset.day = day;

            if (moodData[day]) {
                dayDiv.classList.add(moodData[day]);
            }

            dayDiv.addEventListener('click', function() {
                if (selectedMood.mood) {
                    moodData[day] = selectedMood.mood;
                    updateCalendar();
                    updateChart();
                } else {
                    alert("Please pick a mood first!");
                }
            });

            calendar.appendChild(dayDiv);
        }
    }

    function updateCalendar() {
        generateCalendar();
    }

    document.querySelectorAll('.mood').forEach(moodDiv => {
        moodDiv.addEventListener('click', function() {
            document.querySelectorAll('.mood').forEach(m => m.style.border = '2px solid transparent');
            this.style.border = '2px solid #4CAF50';
            selectedMood.mood = this.dataset.mood;
        });
    });

    // Chart.js setup
    const ctx = document.getElementById('mood-chart').getContext('2d');
    const moodChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['😊 Happy', '😌 Good', '😐 Neutral', '😔 Sad', '😭 Depressed'],
            datasets: [{
                label: 'Mood Count',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#ffeb3b', // happy
                    '#8bc34a', // good
                    '#cddc39', // neutral
                    '#03a9f4', // sad
                    '#e91e63'  // depressed
                ]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    function updateChart() {
        const counts = { happy: 0, good: 0, neutral: 0, sad: 0, depressed: 0 };
        for (const day in moodData) {
            if (counts[moodData[day]] !== undefined) {
                counts[moodData[day]]++;
            }
        }
        moodChart.data.datasets[0].data = [
            counts.happy,
            counts.good,
            counts.neutral,
            counts.sad,
            counts.depressed
        ];
        moodChart.update();
    }

    generateCalendar();
});
