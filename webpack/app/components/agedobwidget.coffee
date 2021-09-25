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

    selector = ".AgeDoBWidget input[id$='-dob-fallback']"
    $("body").on "change", selector, @on_fallback_dob_change

  on_age_selector_change: (event) =>
    console.debug "AgeDoBWidgetController::on_age_selector_change"
    el = event.currentTarget

    # Check if field is required
    wrapper = el.closest ".AgeDoBWidget"
    required =$(wrapper).attr("data-required") == '1' ? 'required' : ''

    # Hide/Show DoB and Age areas
    age_controls = wrapper.querySelector '[id$="_age_controls"]'
    dob_controls = wrapper.querySelector '[id$="_dob_controls"]'

    year_field = wrapper.querySelector('[id$=".years:ignore_empty:record"]')
    dob_field = wrapper.querySelector('[id$=".dob:ignore_empty:record"]')

    if $(el).val() == "age"
      # Age selector active
      $(age_controls).show()
      $(dob_controls).hide()
      year_field.setAttribute 'required', required
      dob_field.removeAttribute 'required'
    else
      $(age_controls).hide()
      $(dob_controls).show()
      year_field.removeAttribute 'required'
      dob_field.setAttribute 'required', required

  on_fallback_dob_change: (event) =>
    console.debug "AgeDoBWidgetController::on_fallback_dob_change"
    el = event.currentTarget

    wrapper = el.closest ".AgeDoBWidget"

    # Select the DoB radio
    dob_selector = wrapper.querySelector("input[id$='_dob_selector']")
    dob_selector.setAttribute 'checked', ''
    $(dob_selector).trigger "change"

    # Copy the value to the DoB control
    dob_field = wrapper.querySelector('[id$=".dob:ignore_empty:record"]')
    dob_field.value = el.value

export default AgeDoBWidgetController
