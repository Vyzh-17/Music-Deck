#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

String songTitle = "";
String artistName = "";

unsigned long lastScrollTime = 0;

int titlePosition = 0;

void setup()
{
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Music Deck");

  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
}

void loop()
{
  receiveMusicData();

  if (millis() - lastScrollTime >= 400)
  {
    lastScrollTime = millis();

    displayMusic();
  }
}

void receiveMusicData()
{
  if (Serial.available() == 0)
  {
    return;
  }

  String message = Serial.readStringUntil('\n');

  message.trim();

  int separatorPosition = message.indexOf('|');

  if (separatorPosition == -1)
  {
    return;
  }

  String newTitle = message.substring(0, separatorPosition);
  String newArtist = message.substring(separatorPosition + 1);

  newTitle.trim();
  newArtist.trim();

  if (newTitle != songTitle || newArtist != artistName)
  {
    songTitle = newTitle;
    artistName = newArtist;

    titlePosition = 0;

    lcd.clear();
  }
}

void displayMusic()
{
  // -----------------------------
  // SONG TITLE - LINE 1
  // -----------------------------

  if (songTitle.length() <= 16)
  {
    lcd.setCursor(0, 0);
    lcd.print("                ");

    lcd.setCursor(0, 0);
    lcd.print(songTitle);
  }
  else
  {
    String scrollingTitle = songTitle + "    ";

    int textLength = scrollingTitle.length();

    for (int i = 0; i < 16; i++)
    {
      int index = (titlePosition + i) % textLength;

      lcd.setCursor(i, 0);
      lcd.print(scrollingTitle[index]);
    }

    titlePosition++;

    if (titlePosition >= textLength)
    {
      titlePosition = 0;
    }
  }

  // -----------------------------
  // ARTIST - LINE 2
  // NO SCROLLING
  // -----------------------------

  lcd.setCursor(0, 1);
  lcd.print("                ");

  lcd.setCursor(0, 1);

  if (artistName.length() <= 16)
  {
    lcd.print(artistName);
  }
  else
  {
    // Show only the first 16 characters
    lcd.print(artistName.substring(0, 16));
  }
}