# TODO

- [] Jazzle UI
- [] Song History/Collection UI
  - [] Downloading audio + sheet music? Not sure, maybe I should allow downloading sheet music but not audio? Maybe both? Maybe neither?
- [] How to get data?
- [] Security, Quality of Life

## BRAINSTORM

- [] I'd like to create a consistent UI though, so that's what I'm going to try to do instead. That means I'm going to have two lines; a top line with metadata and a second line with key and the first phrase
- [] I would have to write a CV program to analyze and determine the first phrase, and then an interface to plot the first phrase. The audio playback can be a small playback button on the bottom and the user will (eventually) be able to select their part from a list in the top right
- [] When something new is revealed, it GLOWS for a bit to indicate that that new thing was just added
- Here's the order I plan on doing things:
  - [] Responsive UI (sm, md, and lg using tailwind); test website using https://www.browserstack.com/responsive
  <!-- - [] One time cookie prompt (for setting key based on instrument); I'm scrapping this for now -->
  - [] Stack (clef + key)
  - [] Functionality using HTMX + backend
  - [] Display the actual music after the final guess or after a correct guess (pop-up)
  - [] Counter
  - [x] Nav-bar menu
  - [] Showcase (grid of Posters with layed-out info)
