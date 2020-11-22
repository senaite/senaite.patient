import TemporaryIdentifierWidgetController from "./components/temporaryidentifierwidget.coffee"

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE PATIENT JS LOADED ***");

  // Initialize controllers
  window.temporary_identifier_widget = new TemporaryIdentifierWidgetController();

});
