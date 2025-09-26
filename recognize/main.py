from celery import Celery

# Create boilerplate celery app and run it in main()
celery_app = Celery(__name__)

def main():
    print("Hello from recognize!")

if __name__ == "__main__":
    main()