import $ from "jquery"

class AgeDoBWidgetController

  constructor: ->
    console.debug "AgeDoBWidgetController::load"

    # bind the event handler to the elements
    @bind_event_handler()

    # Initialize visibility
    radios = ".AgeDoBWidget input[type='radio'][checked]"
    for el in document.querySelectorAll(radios)
      $(el).trigger "change"

    return @

  bind_event_handler: =>
    console.debug "AgeDoBWidgetController::bind_event_handler"
    selector = ".AgeDoBWidget input[type='radio']"
    $("body").on "change", selector, @on_age_selector_change

  on_age_selector_change: (event) =>
    console.debug "AgeDoBWidgetController::on_age_selector_change"
    el = event.currentTarget

    # Hide/Show DoB and Age areas
    wrapper = el.closest ".AgeDoBWidget"
    age_controls = wrapper.querySelector '[id$="_age_controls"]'
    dob_controls = wrapper.querySelector '[id$="_dob_controls"]'
    if $(el).val() == "age"
      # Age selector active
      $(age_controls).show()
      $(dob_controls).hide()
    else
      $(age_controls).hide()
      $(dob_controls).show()

export default AgeDoBWidgetController
