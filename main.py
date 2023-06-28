import sys
from website import create_app

app = create_app()

if __name__ == '__main__':
    if 'clock' in sys.argv:
        from website.clock import scheduled_tasks
        scheduled_tasks()
    else:
        app.run()






