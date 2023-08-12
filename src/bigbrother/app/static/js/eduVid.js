const video = document.getElementById('eduVid-element');

function onTimeStampClick(button)
{
    const time = button.value;
    if(isNaN(time)) return;
    console.log("setting time: " + time)
    video.currentTime = button.value;
}

function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) {
    return 'Invalid time';
  }

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  const formattedTimeParts = [];

  if (hours > 0)
    formattedTimeParts.push(`${hours}h`);

  if (minutes > 0)
    formattedTimeParts.push(`${minutes}m`);

  if (remainingSeconds > 0)
    formattedTimeParts.push(`${remainingSeconds}s`);

  return formattedTimeParts.join('');
}