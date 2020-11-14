

def isMedicalRecordTemporary(self):  # noqa camelcase, but compliant with AT's
    """Returns whether the Medical Record Number is temporary
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    if mrn.get("temporary"):
        return True
    if not mrn.get("value"):
        return True
    return False


def getMedicalRecordNumberValue(self):  # noqa camelcase, but compliant with AT's
    """Returns the medical record number ID
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    return mrn.get("value")
