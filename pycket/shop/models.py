from dataclasses import dataclass
from typing import Optional, Set

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    public = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    seating_plan = models.BinaryField(null=True)
    image = models.ImageField(null=True)
    vendor_note = models.TextField(blank=True)

    class Meta:
        ordering = ["date", "time"]


class SeatReservation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    row = models.IntegerField()
    number = models.IntegerField()


class Ticket(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    seats = models.ManyToManyField(SeatReservation)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["order_date"]


@dataclass(frozen=True)
class SeatingPlan:
    seating_grid: list[list[bool]]
    stage_width: int

    def with_reservations(self, reservations: Set[SeatReservation]):
        grid = [[False if x else None for x in y] for y in self.seating_grid]
        for reservation in reservations:
            grid[reservation.row][reservation.number] = True
        return FilledSeatingPlan(grid, self.stage_width, reservations)


@dataclass(frozen=True)
class FilledSeatingPlan:
    seating_grid: list[list[Optional[bool]]]
    stage_width: int
    reservations: Set[SeatReservation]

    def can_reserve(self, seats):
        for row, number in seats:
            if self.seating_grid[row][number] is not False:
                return False
        return True
