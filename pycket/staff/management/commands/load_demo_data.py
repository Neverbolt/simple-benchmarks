import datetime
import hashlib
import os
import pickle
from decimal import Decimal
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.models import Customer, Event, SeatingPlan, SeatReservation, Ticket

from pycket import settings

SALT = "SALT_WINTERMUTE_MASTER_THESIS"


class Command(BaseCommand):
    help = "Fill the database with realistic demo shop data (customers, events, reservations, tickets)."

    def handle(self, *args, **options):
        self.stdout.write("Creating realistic demo data...")

        # ---------------------------------------------------------------------
        # USERS & CUSTOMERS
        # ---------------------------------------------------------------------
        users_data = [
            ("anna.m", "anna.miller@example.com", "Anna", "Miller"),
            ("ben.s", "ben.schmidt@example.com", "Ben", "Schmidt"),
            ("carla.r", "carla.rodriguez@example.com", "Carla", "Rodriguez"),
            ("daniel.k", "daniel.klein@example.com", "Daniel", "Klein"),
            ("emma.l", "emma.liu@example.com", "Emma", "Liu"),
            ("felix.w", "felix.weber@example.com", "Felix", "Weber"),
            ("greta.h", "greta.hoffmann@example.com", "Greta", "Hoffmann"),
            ("harry.p", "harry.parker@example.com", "Harry", "Parker"),
            ("isabel.t", "isabel.tan@example.com", "Isabel", "Tan"),
            ("jonas.b", "jonas.bauer@example.com", "Jonas", "Bauer"),
        ]

        customers = []

        for username, email, first_name, last_name in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                password = hashlib.sha256(f"{username}{SALT}".encode()).hexdigest()
                user.set_password(password)
                print(f"Created user {username} - {password}")
                user.save()

            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={"balance": Decimal("150.00")},
            )
            customers.append(customer)

        self.stdout.write(f"Created/loaded {len(customers)} customers.")

        # ---------------------------------------------------------------------
        # PREPARE IMAGE PATHS
        # ---------------------------------------------------------------------
        media_root = Path(settings.MEDIA_ROOT)
        demo1_path = media_root / "demo1.png"
        demo2_path = media_root / "demo2.jpg"
        image_paths = [demo1_path, demo2_path]

        # ---------------------------------------------------------------------
        # EVENTS & SEATING PLANS
        # ---------------------------------------------------------------------
        today = timezone.localdate()

        events_data = [
            {
                "name": "Indie Rock Night",
                "date": today + datetime.timedelta(days=5),
                "time": datetime.time(hour=20, minute=0),
                "location": "City Club",
                "description": "Local indie bands playing original songs. <a href='/event/1/resource/cm9jay5wbmc='>Preview</a>",
                "public": True,
                "price": Decimal("18.00"),
                "vendor_note": "Standing area in the back.",
                "rows": 8,
                "cols": 15,
                "stage_width": 12,
            },
            {
                "name": "Acoustic Evening",
                "date": today + datetime.timedelta(days=8),
                "time": datetime.time(hour=19, minute=30),
                "location": "Old Town Theater",
                "description": "Unplugged sets from singer-songwriters.",
                "public": True,
                "price": Decimal("24.00"),
                "vendor_note": "No late entry during performances.",
                "rows": 10,
                "cols": 18,
                "stage_width": 14,
            },
            {
                "name": "Saturday Comedy Special",
                "date": today + datetime.timedelta(days=12),
                "time": datetime.time(hour=21, minute=0),
                "location": "Comedy Cellar",
                "description": "Four stand-up comedians, one hilarious night.",
                "public": True,
                "price": Decimal("22.00"),
                "vendor_note": "Two-drink minimum.",
                "rows": 7,
                "cols": 12,
                "stage_width": 10,
            },
            {
                "name": "Tech Conference 2025 - Day 1",
                "date": today + datetime.timedelta(days=20),
                "time": datetime.time(hour=9, minute=0),
                "location": "Convention Center Hall A",
                "description": "Talks on AI, cloud computing, and security.",
                "public": True,
                "price": Decimal("199.00"),
                "vendor_note": "Registration opens at 8:00.",
                "rows": 20,
                "cols": 30,
                "stage_width": 25,
            },
            {
                "name": "Tech Conference 2025 - Day 2",
                "date": today + datetime.timedelta(days=21),
                "time": datetime.time(hour=9, minute=0),
                "location": "Convention Center Hall A",
                "description": "Workshops and hands-on sessions.",
                "public": True,
                "price": Decimal("219.00"),
                "vendor_note": "Workshop rooms announced on site.",
                "rows": 20,
                "cols": 30,
                "stage_width": 25,
            },
            {
                "name": "Shakespeare in the Park",
                "date": today + datetime.timedelta(days=15),
                "time": datetime.time(hour=18, minute=30),
                "location": "Riverside Park Stage",
                "description": "Outdoor performance of a classic play.",
                "public": True,
                "price": Decimal("12.00"),
                "vendor_note": "Bring blankets, limited seating.",
                "rows": 12,
                "cols": 20,
                "stage_width": 16,
            },
            {
                "name": "Sunday Jazz Brunch",
                "date": today + datetime.timedelta(days=10),
                "time": datetime.time(hour=11, minute=0),
                "location": "Blue Note Café",
                "description": "Smooth jazz with brunch buffet.",
                "public": True,
                "price": Decimal("35.00"),
                "vendor_note": "Buffet included in ticket price.",
                "rows": 6,
                "cols": 10,
                "stage_width": 8,
            },
            {
                "name": "Charity Gala Dinner",
                "date": today + datetime.timedelta(days=30),
                "time": datetime.time(hour=19, minute=0),
                "location": "Grand Hotel Ballroom",
                "description": "Black-tie evening with live auction.",
                "public": True,
                "price": Decimal("500.00"),
                "vendor_note": "Formal dress code, invitation only. "
                + os.environ["FLAG_EVENT"],
                "rows": 12,
                "cols": 14,
                "stage_width": 10,
            },
        ]

        events = []

        for idx, data in enumerate(events_data):
            event, created = Event.objects.get_or_create(
                name=data["name"],
                date=data["date"],
                defaults={
                    "time": data["time"],
                    "location": data["location"],
                    "description": data["description"],
                    "public": data["public"],
                    "price": data["price"],
                    "vendor_note": data["vendor_note"],
                },
            )

            # Build a rectangular seating grid with all seats present (True)
            rows = data["rows"]
            cols = data["cols"]
            seating_grid = [[True for _ in range(cols)] for _ in range(rows)]
            seating_plan = SeatingPlan(
                seating_grid=seating_grid, stage_width=data["stage_width"]
            )
            event.seating_plan = pickle.dumps(seating_plan)

            if not event.image:
                img_path = image_paths[idx % len(image_paths)]
                if img_path.exists():
                    with img_path.open("rb") as f:
                        # save(name, content, save=True)
                        event.image.save(img_path.name, File(f), save=False)
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Image file not found: {img_path}")
                    )

            event.save()

            events.append(event)

        self.stdout.write(f"Created/loaded {len(events)} events with seating plans.")

        # ---------------------------------------------------------------------
        # SEAT RESERVATIONS
        # ---------------------------------------------------------------------
        # We'll create some reserved seats scattered across front, middle, and back.
        all_reservations = []

        def reserve_block(event, row, seat_start, seat_end):
            """Reserve seats [seat_start, seat_end) on a given row for an event."""
            nonlocal all_reservations
            for number in range(seat_start, seat_end):
                reservation, _ = SeatReservation.objects.get_or_create(
                    event=event,
                    row=row,
                    number=number,
                )
                all_reservations.append(reservation)

        for event, data in zip(events, events_data):
            rows = data["rows"]
            cols = data["cols"]

            # Front row block
            reserve_block(event, row=0, seat_start=2, seat_end=min(8, cols))

            # Middle row block
            mid_row = rows // 2
            reserve_block(event, row=mid_row, seat_start=4, seat_end=min(12, cols))

            # Back row block
            last_row = rows - 1
            reserve_block(event, row=last_row, seat_start=0, seat_end=min(5, cols))

        self.stdout.write(f"Created/loaded {len(all_reservations)} seat reservations.")

        # ---------------------------------------------------------------------
        # TICKETS
        # ---------------------------------------------------------------------
        # Clear old demo tickets for these events to avoid duplicates.
        Ticket.objects.filter(event__in=events).delete()

        tickets_created = []

        # Helper: create a ticket for a customer & event with a set of (row, seat_numbers)
        def create_ticket(customer, event, seat_specs, note):
            """
            seat_specs: list of tuples (row, [seat_number, ...])
            """
            seat_objs = []
            for row, seat_numbers in seat_specs:
                qs = SeatReservation.objects.filter(
                    event=event,
                    row=row,
                    number__in=seat_numbers,
                )
                seat_objs.extend(list(qs))

            if not seat_objs:
                return None

            total = event.price * len(seat_objs)
            ticket = Ticket.objects.create(
                customer=customer,
                event=event,
                total=total,
                note=note,
            )
            ticket.seats.add(*seat_objs)
            return ticket

        # Some nice combinations
        # Indie Rock Night
        t = create_ticket(
            customers[0],
            events[0],
            [(0, [2, 3, 4])],
            "Friends night out." + os.environ["FLAG_TICKET"],
        )
        if t:
            tickets_created.append(t)

        t = create_ticket(
            customers[1],
            events[0],
            [(4, [6, 7])],
            "Date night.",
        )
        if t:
            tickets_created.append(t)

        # Acoustic Evening
        t = create_ticket(
            customers[2],
            events[1],
            [(0, [5, 6]), (5, [8, 9])],
            "Booked early for best seats.",
        )
        if t:
            tickets_created.append(t)

        # Saturday Comedy Special
        t = create_ticket(
            customers[3],
            events[2],
            [(0, [2, 3, 4, 5])],
            "Birthday celebration.",
        )
        if t:
            tickets_created.append(t)

        t = create_ticket(
            customers[4],
            events[2],
            [(3, [4, 5])],
            "Work colleagues.",
        )
        if t:
            tickets_created.append(t)

        # Tech Conference Day 1 & 2
        t = create_ticket(
            customers[5],
            events[3],
            [(10, [10, 11, 12])],
            "Company-sponsored attendance.",
        )
        if t:
            tickets_created.append(t)

        t = create_ticket(
            customers[5],
            events[4],
            [(10, [10, 11, 12])],
            "Same group, second day.",
        )
        if t:
            tickets_created.append(t)

        t = create_ticket(
            customers[6],
            events[3],
            [(5, [14, 15])],
            "Interested in AI track.",
        )
        if t:
            tickets_created.append(t)

        # Shakespeare in the Park
        t = create_ticket(
            customers[7],
            events[5],
            [(0, [3, 4]), (6, [5, 6])],
            "Family outing.",
        )
        if t:
            tickets_created.append(t)

        # Sunday Jazz Brunch
        t = create_ticket(
            customers[8],
            events[6],
            [(0, [2, 3])],
            "Window seats.",
        )
        if t:
            tickets_created.append(t)

        t = create_ticket(
            customers[9],
            events[6],
            [(2, [4, 5, 6])],
            "Reserved for friends.",
        )
        if t:
            tickets_created.append(t)

        self.stdout.write(f"Created {len(tickets_created)} tickets.")

        self.stdout.write(
            self.style.SUCCESS("Realistic demo data loaded successfully.")
        )
