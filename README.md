todo: add chat bot gpt3
todo: add database
database plan:
restaurant id, every restaurant has many channels (text channels to update)

`add command:
adds restaurant
every restaurant can have multiple channels where the status updates are sent
evry 60s gets all restaurants from db with channels, updates the restaurants status, sends update if required

`remove command:
removes restaurant

`list command:
lists all restaurants in guild/channel