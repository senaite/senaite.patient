# -*- coding: utf-8 -*-

from bika.lims.api import get_portal
from senaite.patient import is_installed
from senaite.patient import logger
from senaite.patient.setuphandlers import setup_id_formatting
from senaite.patient.setuphandlers import setup_navigation_types
from senaite.patient.setuphandlers import setup_workflow


def afterUpgradeStepHandler(event):
    """Event handler that is executed after running an upgrade step of senaite.core
    """
    if not is_installed():
        return
    logger.info("Run senaite.patient.afterUpgradeStepHandler ...")
    portal = get_portal()
    setup_navigation_types(portal)
    setup_id_formatting(portal)
    setup_workflow(portal)
    logger.info("Run senaite.patient.afterUpgradeStepHandler [DONE]")
