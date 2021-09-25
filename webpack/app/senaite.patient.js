import TemporaryIdentifierWidgetController from "./components/temporaryidentifierwidget.coffee"
import AgeDoBWidgetController from "./components/agedobwidget.coffee"

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE PATIENT JS LOADED ***");

  // Initialize controllers
  window.temporary_identifier_widget = new TemporaryIdentifierWidgetController();
  window.age_dob_widget = new AgeDoBWidgetController();

});
