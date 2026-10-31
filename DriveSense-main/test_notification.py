
from winotify import Notification

notification = Notification(
    app_id="DriveSense",
    title="DriveSense — Highway Alert",
    msg="Highway ahead! Stay alert and monitor the road."
)

notification.show()

print("Highway notification sent.")
