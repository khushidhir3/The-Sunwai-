"""
cases — Case management models.
"""
from django.conf import settings
from django.db import models


class Case(models.Model):
    """A court case with parties and advocates."""

    class CaseType(models.TextChoices):
        CIVIL = 'civil', 'Civil Suit'
        CRIMINAL = 'criminal', 'Criminal Case'
        WRIT = 'writ', 'Writ Petition'
        APPEAL = 'appeal', 'Appeal'
        ARBITRATION = 'arbitration', 'Arbitration'
        FAMILY = 'family', 'Family Matter'
        COMMERCIAL = 'commercial', 'Commercial Dispute'

    class Status(models.TextChoices):
        FILED = 'filed', 'Filed'
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        RESERVED = 'reserved', 'Reserved for Orders'
        DISPOSED = 'disposed', 'Disposed'
        ARCHIVED = 'archived', 'Archived'

    class Stage(models.TextChoices):
        FILING = 'filing', 'Filing'
        NOTICE = 'notice', 'Notice Stage'
        PLEADINGS = 'pleadings', 'Pleadings'
        CASE_MGMT = 'case_mgmt', 'Case Management'
        TRIAL = 'trial', 'Trial'
        ARGUMENTS = 'arguments', 'Arguments'
        JUDGMENT = 'judgment', 'Judgment'

    case_no = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(
        max_length=300,
        help_text='e.g. "Smith v. Jones Corporation"',
    )
    case_type = models.CharField(max_length=20, choices=CaseType.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.FILED,
    )
    stage = models.CharField(
        max_length=20, choices=Stage.choices, default=Stage.FILING,
    )
    filing_date = models.DateField(auto_now_add=True)
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_cases',
        limit_choices_to={'role': 'judge'},
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'cases'

    def __str__(self):
        return f'{self.case_no} — {self.title}'

    @property
    def petitioners(self):
        return self.parties.filter(party_type=Party.PartyType.PETITIONER)

    @property
    def respondents(self):
        return self.parties.filter(party_type=Party.PartyType.RESPONDENT)

    @property
    def short_title(self):
        """e.g. 'Smith v. Jones'"""
        pet = self.petitioners.first()
        res = self.respondents.first()
        if pet and res:
            return f'{pet.name} v. {res.name}'
        return self.title[:60]


class Party(models.Model):
    """A party to a case (petitioner or respondent)."""

    class PartyType(models.TextChoices):
        PETITIONER = 'petitioner', 'Petitioner'
        RESPONDENT = 'respondent', 'Respondent'
        INTERVENOR = 'intervenor', 'Intervenor'

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='parties')
    name = models.CharField(max_length=200)
    party_type = models.CharField(max_length=20, choices=PartyType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='party_roles',
    )
    advocate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='represented_parties',
        limit_choices_to={'role': 'advocate'},
    )

    class Meta:
        verbose_name_plural = 'parties'
        ordering = ['party_type', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_party_type_display()})'


class Pleading(models.Model):
    """Uploaded pleadings / documents for a case."""

    class DocType(models.TextChoices):
        PLAINT = 'plaint', 'Plaint'
        WRITTEN_STATEMENT = 'ws', 'Written Statement'
        REPLY = 'reply', 'Reply'
        REJOINDER = 'rejoinder', 'Rejoinder'
        APPLICATION = 'application', 'Application'
        AFFIDAVIT = 'affidavit', 'Affidavit'
        EXHIBIT = 'exhibit', 'Exhibit'
        OTHER = 'other', 'Other'

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='pleadings')
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    file = models.FileField(upload_to='pleadings/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.title} — {self.case.case_no}'
