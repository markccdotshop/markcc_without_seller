$(document).ready(function () {
    var taskProgress = {};
    var completedTasks = 0;
    var duplicates = [];
    var errors = [];

    function updateOverallProgress() {
        var totalProgress = 0;
        var taskCount = Object.keys(taskProgress).length;
        for (var taskId in taskProgress) {
            totalProgress += taskProgress[taskId];
        }
        var overallProgress = taskCount > 0 ? totalProgress / taskCount : 0;
        $('#progressBar').css('width', overallProgress + '%');
        $('#progressText').text(overallProgress.toFixed(2) + '% Complete');
    }

    function showResultsButton() {
        $('#showResultsButtons').show();
    }

    function checkAllTasksCompleted(totalTasks) {
        if (completedTasks === totalTasks) {
            showResultsButton();
            $('#uploadForm').find('button[name="upload"]').text('Upload').prop('disabled', false);
        }
    }

    function trackProgress(taskId, totalTasks) {
        var interval = setInterval(function () {
            $.ajax({
                url: '/seller/categories/celery-progress/' + taskId + '/',
                success: function (data) {
                    taskProgress[taskId] = parseInt(data.progress.percent);
                    updateOverallProgress();
    
                    if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
                        clearInterval(interval);
                        completedTasks++;
                        checkAllTasksCompleted(totalTasks);
    
                        if (data.state === 'SUCCESS') {
                            displayResults(data.result);
                        } else {
                            $('#messageContainer').html('<div class="error-message">Upload failed.</div>');
                            clearMessageAfterDelay(5000);
                        }
                    }
                },
                error: function () {
                    clearInterval(interval);
                    $('#messageContainer').html('<div class="error-message">Error tracking progress.</div>');
                    clearMessageAfterDelay(5000);
                }
            });
        }, 2000);
    }

    function displayResults(result) {
        if (result.duplicates && result.duplicates.length > 0) {
            duplicates = duplicates.concat(result.duplicates);
            $('#showDuplicates').show().text('Show Duplicates (' + duplicates.length + ')');
        }
        if (result.errors && result.errors.length > 0) {
            errors = errors.concat(result.errors);
            $('#showErrors').show().text('Show Errors (' + errors.length + ')');
        }
    }

    $('#showDuplicates').click(function() {
        var content = '<h4>Duplicates (' + duplicates.length + '):</h4><p>' + duplicates.join('<br>') + '</p>';
        $('#modalContent').html(content);
        $('#resultsModal').modal('show');
    });

    $('#showErrors').click(function() {
        var errorContent = errors.map(function(error) {
            return error.data;
        }).join('<br>');
        var content = '<h4>Errors (' + errors.length + '):</h4><p>' + errorContent + '</p>';
        $('#modalContent').html(content);
        $('#resultsModal').modal('show');
    });

    $('#copyResults').click(function() {
        var content = $('#modalContent').text();
        navigator.clipboard.writeText(content).then(function() {
            console.log('Async: Copying to clipboard was successful!');
            alert('Results copied to clipboard.');
        }, function(err) {
            console.error('Async: Could not copy text: ', err);
            alert('Failed to copy text.');
        });
    });

    function clearMessageAfterDelay(delay) {
        setTimeout(function() {
            $('#messageContainer').html('');
        }, delay);
    }

    $('#uploadForm').submit(function (e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var $uploadButton = $(this).find('button[name="upload"]');

        $uploadButton.text('Uploading...').prop('disabled', true);

        $.ajax({
            type: 'POST',
            url: '/seller/categories/upload/cards/',
            data: formData,
            success: function (response) {
                if (response.task_ids && response.task_ids.length > 0) {
                    $('#progressBarContainer').show();
                    $('#progressText').show().text('0% Complete');
                    response.task_ids.forEach(function(taskId) {
                        trackProgress(taskId, response.task_ids.length);
                    });
                } else {
                    $('#messageContainer').html('<div class="error-message">' + (response.message || 'Unexpected error') + '</div>');
                    $uploadButton.text('Upload').prop('disabled', false);
                    clearMessageAfterDelay(5000);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var errorMessage = 'An error occurred during submission.';
            
                if (jqXHR.status === 0) {
                    errorMessage = 'Not connected. Please verify your network connection.';
                } else if (jqXHR.status == 404) {
                    errorMessage = 'Requested page not found. [404]';
                } else if (jqXHR.status == 500) {
                    errorMessage = 'Internal Server Error [500].';
                } else if (textStatus === 'parsererror') {
                    errorMessage = 'Requested JSON parse failed.';
                } else if (textStatus === 'timeout') {
                    errorMessage = 'Time out error.';
                } else if (textStatus === 'abort') {
                    errorMessage = 'Ajax request aborted.';
                } else if (jqXHR.status == 400) {
                    errorMessage = jqXHR.responseJSON.error;
                } else {
                    errorMessage = 'Uncaught Error.\n' + jqXHR.responseText;
                }
            
                $('#messageContainer').html('<div class="alert alert-danger">' + errorMessage + '</div>');
                $uploadButton.text('Upload').prop('disabled', false);
                clearMessageAfterDelay(5000);
            }
        });
    });
});
