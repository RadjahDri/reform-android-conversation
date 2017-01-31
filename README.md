# Reform Android Conversation
## Description
This is a forensic simple tool to reforme all sms conversation of android device from its filesystem dump. It can display conversations in console or in HTML format.

Two files are used to this:
- mmssms.db: store all sms
- contacts.db: store contact informations (Optionnal)

If you have any question about my works, don't hesitate to contact me by issues.

## Usage
### Preparation
First you must have sqlitebrowser to extract csv files from database files:
```
sudo apt-get install sqlitebrowser
```
Open each database file, select tab "Database_Structure", left click on table and "Export as CSV file". Column name in first line must be selected, field separator must be ',' and quote character must be '"'.

### Launch
```
reformConversation.py csvContacts csvSMS [file.html]
```
The first arguments must be path to sms CSV file. Then it can be specify path to contacts CSV file to improve displayed informations. The last arguments can be path to output HTML file (ended by .html) If it isn't give ouput is in console.

## Ouput
### Received/sent
In each display type, the sms at left are received by inspected device and the sms at right are sent.
```
+33696573878:
                                      Sun 03/01/2017 22:37
                                      Hi, how are you ? When can
                                      you back at home ?

  Mon 05/01/2017 12:00
  Fine and you ? I don't known
  I have much work.
```

### Contacts
If contact CSV file are specified, for each number link with known contact, name is displayed.
```
Cecile Landry(+33651835203):

  Tue 03/01/2017 15:14
  ...
```

### HTML
In HTML display, it is possible to expend and collapse conversation for more comprehension. The two buttons in top of page do that for all conversations at once.
