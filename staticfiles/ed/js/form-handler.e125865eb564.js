document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('yourFormId');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                // Handle success (e.g., display a success message)
            })
            .catch((error) => {
                console.error('Error:', error);
                // Handle errors (e.g., display an error message)
            });
        });
    }
});
