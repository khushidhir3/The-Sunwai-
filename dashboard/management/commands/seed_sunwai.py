"""Seed command for The Sunwai e-Portal."""
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from accounts.models import User
from cases.models import Case, Party, Pleading
from scheduling.models import Courtroom, HearingSlot
from hearings.models import Hearing, PreHearingChecklist, ChecklistItem, HearingNote, ChatMessage
from directions.models import DirectionTemplate, Direction, ComplianceTask


class Command(BaseCommand):
    help = 'Seed database with realistic initial Case Management Portal data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding The Sunwai portal data...')

        # ── 1. Create Users ──
        admin, _ = User.objects.get_or_create(
            email='admin@thesunwai.court',
            defaults={
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin.set_password('sunwai2024')
        admin.save()

        judge, _ = User.objects.get_or_create(
            email='judge@thesunwai.court',
            defaults={
                'first_name': 'Vikramaditya',
                'last_name': 'Roy',
                'role': User.Role.JUDGE,
                'court_designation': 'Presiding Judge, Commercial Division',
                'phone': '+91 11 2338 4901',
                'is_staff': True,
            }
        )
        judge.set_password('sunwai2024')
        judge.save()

        judge2, _ = User.objects.get_or_create(
            email='judge2@thesunwai.court',
            defaults={
                'first_name': 'Arundhati',
                'last_name': 'Banerjee',
                'role': User.Role.JUDGE,
                'court_designation': 'Presiding Judge, Civil Roster Bench III',
                'phone': '+91 11 2338 4902',
                'is_staff': True,
            }
        )
        judge2.set_password('sunwai2024')
        judge2.save()

        registrar, _ = User.objects.get_or_create(
            email='registrar@thesunwai.court',
            defaults={
                'first_name': 'K. S.',
                'last_name': 'Narayanan',
                'role': User.Role.REGISTRAR,
                'court_designation': 'Registrar, Pre-Trial Case Management',
                'phone': '+91 11 2338 4910',
                'is_staff': True,
            }
        )
        registrar.set_password('sunwai2024')
        registrar.save()

        advocate1, _ = User.objects.get_or_create(
            email='advocate@thesunwai.court',
            defaults={
                'first_name': 'Meenakshi',
                'last_name': 'Sundaram',
                'role': User.Role.ADVOCATE,
                'bar_number': 'D/1482/2011',
                'phone': '+91 98101 23456',
            }
        )
        advocate1.set_password('sunwai2024')
        advocate1.save()

        advocate2, _ = User.objects.get_or_create(
            email='counsel2@thesunwai.court',
            defaults={
                'first_name': 'Arjun',
                'last_name': 'Kapoor',
                'role': User.Role.ADVOCATE,
                'bar_number': 'D/2045/2015',
                'phone': '+91 98202 34567',
            }
        )
        advocate2.set_password('sunwai2024')
        advocate2.save()

        litigant1, _ = User.objects.get_or_create(
            email='litigant@thesunwai.court',
            defaults={
                'first_name': 'Bharat Heavy',
                'last_name': 'Infra Ltd.',
                'role': User.Role.LITIGANT,
                'phone': '+91 11 4150 9000',
            }
        )
        litigant1.set_password('sunwai2024')
        litigant1.save()

        litigant2, _ = User.objects.get_or_create(
            email='litigant2@thesunwai.court',
            defaults={
                'first_name': 'Apex Metro',
                'last_name': 'Consortia Corp.',
                'role': User.Role.LITIGANT,
                'phone': '+91 11 4150 9111',
            }
        )
        litigant2.set_password('sunwai2024')
        litigant2.save()

        # ── 2. Create Courtrooms ──
        c1, _ = Courtroom.objects.get_or_create(name='Courtroom 1 (Hybrid)', defaults={'location': 'Court Block A, Ground Floor', 'capacity': 45, 'is_virtual': True})
        c2, _ = Courtroom.objects.get_or_create(name='Courtroom 2', defaults={'location': 'Court Block A, First Floor', 'capacity': 35})
        c3, _ = Courtroom.objects.get_or_create(name='Courtroom 3 (Bench Chamber)', defaults={'location': 'West Wing, Second Floor', 'capacity': 25})
        c4, _ = Courtroom.objects.get_or_create(name='Courtroom 4 (Commercial)', defaults={'location': 'East Wing, Ground Floor', 'capacity': 50})

        # ── 3. Direction Templates ──
        templates_data = [
            ('Admission/Denial of Documents', 'pleadings', 'Parties shall file affidavits of admission and denial of documents within {days} days from today.'),
            ('Exchange of Witness Affidavits', 'evidence', 'Plaintiff and Defendant shall exchange affidavits in evidence of PW-1 and DW-1 within {days} days.'),
            ('Joint Framing of Issues', 'issues', 'Counsel for both sides shall confer and tender a joint memorandum of agreed issues within {days} days.'),
            ('Reference to Court Mediation', 'case_management', 'Matter is referred to Delhi High Court Mediation Centre. Report to be placed before registry within {days} days.'),
            ('Filing of Skeleton Submissions', 'case_management', 'Learned counsel shall file concise skeleton arguments not exceeding 5 pages within {days} days.'),
        ]
        for title, cat, tmpl in templates_data:
            DirectionTemplate.objects.get_or_create(
                title=title,
                defaults={'category': cat, 'body': tmpl, 'is_active': True}
            )

        # ── 4. Create Cases ──
        today = date.today()

        case1, _ = Case.objects.get_or_create(
            case_no='CS(COMM) 104/2024',
            defaults={
                'title': 'Bharat Heavy Infra Ltd. v. Apex Metro Consortia Corp.',
                'case_type': Case.CaseType.COMMERCIAL,
                'stage': Case.Stage.CASE_MGMT,
                'status': Case.Status.ACTIVE,
                'judge': judge,
                'description': 'Commercial dispute arising from delay and liquidated damages under an infrastructure master procurement agreement. Plaintiff seeks recovery of ₹4.85 Crores with interest and restraint against encashment of performance bank guarantees.',
            }
        )

        case2, _ = Case.objects.get_or_create(
            case_no='ARB.P. 88/2024',
            defaults={
                'title': 'Southern Expressways Ltd. v. National Concessions Authority',
                'case_type': Case.CaseType.ARBITRATION,
                'stage': Case.Stage.PLEADINGS,
                'status': Case.Status.ACTIVE,
                'judge': judge,
                'description': 'Petition under Section 11(6) of the Arbitration and Conciliation Act seeking constitution of an arbitral tribunal for adjudication of tollway escalation claims.',
            }
        )

        case3, _ = Case.objects.get_or_create(
            case_no='CS(OS) 219/2024',
            defaults={
                'title': 'Oberoi Heritage Properties v. Municipal Corporation of Delhi',
                'case_type': Case.CaseType.CIVIL,
                'stage': Case.Stage.CASE_MGMT,
                'status': Case.Status.ACTIVE,
                'judge': judge2,
                'description': 'Suit for declaration and permanent injunction challenging municipal regularization notices and structural conservation orders.',
            }
        )

        case4, _ = Case.objects.get_or_create(
            case_no='OMP(COMM) 45/2024',
            defaults={
                'title': 'Matrix Telecom Solutions v. Department of Telecommunications',
                'case_type': Case.CaseType.COMMERCIAL,
                'stage': Case.Stage.PLEADINGS,
                'status': Case.Status.PENDING,
                'judge': judge,
                'description': 'Commercial challenge regarding spectrum fee computation and adjusted gross revenue reconciliations.',
            }
        )

        # ── 5. Create Parties ──
        Party.objects.get_or_create(
            case=case1,
            party_type=Party.PartyType.PETITIONER,
            name='Bharat Heavy Infra Ltd.',
            defaults={'advocate': advocate1, 'user': litigant1}
        )
        Party.objects.get_or_create(
            case=case1,
            party_type=Party.PartyType.RESPONDENT,
            name='Apex Metro Consortia Corp.',
            defaults={'advocate': advocate2, 'user': litigant2}
        )

        Party.objects.get_or_create(
            case=case2,
            party_type=Party.PartyType.PETITIONER,
            name='Southern Expressways Ltd.',
            defaults={'advocate': advocate1}
        )
        Party.objects.get_or_create(
            case=case2,
            party_type=Party.PartyType.RESPONDENT,
            name='National Concessions Authority',
            defaults={'advocate': advocate2}
        )

        # ── 6. Create Pleadings ──
        p1, _ = Pleading.objects.get_or_create(
            case=case1,
            title='Plaint with Statement of Claim',
            defaults={
                'uploaded_by': advocate1,
                'doc_type': Pleading.DocType.PLAINT,
                'description': 'Plaint under Order VII Rule 1 CPC with statement of value and prayer clause.',
            }
        )
        if not p1.file:
            p1.file.save('plaint_104.pdf', ContentFile(b'%PDF-1.4 sample plaint content'))

        p2, _ = Pleading.objects.get_or_create(
            case=case1,
            title='Written Statement & Preliminary Objections',
            defaults={
                'uploaded_by': advocate2,
                'doc_type': Pleading.DocType.WRITTEN_STATEMENT,
                'description': 'Defence of respondent contesting liability and raising counter-claims.',
            }
        )
        if not p2.file:
            p2.file.save('ws_104.pdf', ContentFile(b'%PDF-1.4 sample written statement content'))

        p3, _ = Pleading.objects.get_or_create(
            case=case1,
            title='Joint Memorandum of Agreed Issues & Timetable',
            defaults={
                'uploaded_by': advocate1,
                'doc_type': Pleading.DocType.EXHIBIT,
                'description': 'Proposed issues framed under Order X CPC.',
            }
        )
        if not p3.file:
            p3.file.save('issues_104.pdf', ContentFile(b'%PDF-1.4 sample issues content'))

        # ── 7. Create Hearing Slots ──
        slot1, _ = HearingSlot.objects.get_or_create(
            case=case1,
            date=today,
            start_time=time(10, 30),
            defaults={
                'end_time': time(11, 15),
                'judge': judge,
                'courtroom': c1,
                'purpose': 'Case Management Hearing (Order X-A CPC)',
                'status': HearingSlot.SlotStatus.SCHEDULED,
            }
        )

        slot2, _ = HearingSlot.objects.get_or_create(
            case=case2,
            date=today,
            start_time=time(11, 30),
            defaults={
                'end_time': time(12, 15),
                'judge': judge,
                'courtroom': c1,
                'purpose': 'Pre-Trial Review & Settlement Conference',
                'status': HearingSlot.SlotStatus.SCHEDULED,
            }
        )

        slot3, _ = HearingSlot.objects.get_or_create(
            case=case3,
            date=today,
            start_time=time(14, 0),
            defaults={
                'end_time': time(14, 45),
                'judge': judge2,
                'courtroom': c2,
                'purpose': 'Framing of Preliminary Issues',
                'status': HearingSlot.SlotStatus.CONFIRMED,
            }
        )

        slot4, _ = HearingSlot.objects.get_or_create(
            case=case4,
            date=today + timedelta(days=2),
            start_time=time(10, 30),
            defaults={
                'end_time': time(11, 15),
                'judge': judge,
                'courtroom': c1,
                'purpose': 'First Case Management Conference',
                'status': HearingSlot.SlotStatus.SCHEDULED,
            }
        )

        # ── 8. Create Hearings & Checklists ──
        hearing1, _ = Hearing.objects.get_or_create(slot=slot1)
        checklist1, _ = PreHearingChecklist.objects.get_or_create(hearing=hearing1)
        ChecklistItem.objects.get_or_create(
            checklist=checklist1,
            description='All pleadings filed and served on opposing counsel',
            defaults={'category': ChecklistItem.ItemCategory.PLEADINGS, 'is_completed': True, 'completed_by': registrar}
        )
        ChecklistItem.objects.get_or_create(
            checklist=checklist1,
            description='Statements of admission and denial of documents exchanged',
            defaults={'category': ChecklistItem.ItemCategory.ADMISSIONS, 'is_completed': True, 'completed_by': advocate1}
        )
        ChecklistItem.objects.get_or_create(
            checklist=checklist1,
            description='Draft joint issues proposed and submitted to registry',
            defaults={'category': ChecklistItem.ItemCategory.ISSUES, 'is_completed': False}
        )
        ChecklistItem.objects.get_or_create(
            checklist=checklist1,
            description='List of prospective witnesses exchanged',
            defaults={'category': ChecklistItem.ItemCategory.WITNESS_LIST, 'is_completed': False}
        )

        HearingNote.objects.get_or_create(
            hearing=hearing1,
            judge=judge,
            content='Parties have largely narrowed factual controversy down to liquidated damages clause 14.2. Recommended 3 weeks for evidence affidavits.'
        )

        ChatMessage.objects.get_or_create(
            hearing=hearing1,
            sender=registrar,
            message='Registry confirms both learned counsel are connected and in attendance via hybrid audio-video stream.'
        )

        hearing2, _ = Hearing.objects.get_or_create(slot=slot2)
        hearing3, _ = Hearing.objects.get_or_create(slot=slot3)

        # ── 9. Directions & Compliance Tasks ──
        d1, _ = Direction.objects.get_or_create(
            hearing=hearing1,
            serial_no=1,
            defaults={
                'text': 'Petitioner shall file affidavit in chief of PW-1 along with copies of vouchers within 3 weeks.',
                'deadline': today + timedelta(days=21),
                'status': Direction.DirectionStatus.ISSUED,
                'assigned_to': advocate1,
            }
        )
        ComplianceTask.objects.get_or_create(
            direction=d1,
            defaults={'description': 'File evidence affidavit of PW-1', 'assigned_to': advocate1, 'status': ComplianceTask.TaskStatus.PENDING}
        )

        d2, _ = Direction.objects.get_or_create(
            hearing=hearing1,
            serial_no=2,
            defaults={
                'text': 'Respondent to produce original site measurement books for registry inspection.',
                'deadline': today + timedelta(days=14),
                'status': Direction.DirectionStatus.IN_PROGRESS,
                'assigned_to': advocate2,
            }
        )
        ComplianceTask.objects.get_or_create(
            direction=d2,
            defaults={'description': 'Produce original measurement logbook', 'assigned_to': advocate2, 'status': ComplianceTask.TaskStatus.PENDING}
        )

        d3, _ = Direction.objects.get_or_create(
            hearing=hearing2,
            serial_no=1,
            defaults={
                'text': 'Parties to confer on mutually agreed arbitrator name within 10 days.',
                'deadline': today + timedelta(days=10),
                'status': Direction.DirectionStatus.ISSUED,
                'assigned_to': advocate1,
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded The Sunwai database with realistic case management data!'))
