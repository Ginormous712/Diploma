import io
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_ticket_pdf(ticket):
    """
    Генерує PDF файл квитка на основі об'єкта ticket.
    Повертає байтовий потік PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Заголовок
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, height - 1 * inch, "Airline Ticket")

    # Інформація про пасажира
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.5 * inch, f"Passenger: {ticket.user.username}")

    flight = ticket.flight
    c.drawString(1 * inch, height - 1.8 * inch, f"Airline: {flight.airline.name}")
    c.drawString(1 * inch, height - 2.1 * inch, f"Flight Number: {flight.flight_number}")
    c.drawString(1 * inch, height - 2.4 * inch, f"From: {flight.departure_airport.name} ({flight.departure_airport.code})")
    c.drawString(1 * inch, height - 2.7 * inch, f"To: {flight.arrival_airport.name} ({flight.arrival_airport.code})")
    c.drawString(1 * inch, height - 3.0 * inch, f"Departure: {flight.departure_time.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(1 * inch, height - 3.3 * inch, f"Seat Number: {ticket.seat_number}")
    c.drawString(1 * inch, height - 3.6 * inch, f"Issued On: {ticket.issued_date.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(1 * inch, height - 3.9 * inch, f"Booking ID: {ticket.id}")

    # Генерація QR-коду
    qr_data = f"TicketID:{ticket.id};User:{ticket.user.username};Flight:{flight.flight_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Вставка QR-коду (PIL Image) у PDF
    c.drawInlineImage(img, width - 2.5 * inch, height - 3.5 * inch, 2 * inch, 2 * inch)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
