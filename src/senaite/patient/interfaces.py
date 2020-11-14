
from senaite.lims.interfaces import ISenaiteLIMS


class ISenaitePatientLayer(ISenaiteLIMS):
    """Zope 3 browser Layer interface specific for senaite.patient
    This interface is referred in profiles/default/browserlayer.xml.
    All views and viewlets register against this layer will appear in the site
    only when the add-on installer has been run.
    """
