FixNow sample datasets

1. technicians.csv: 21 fictional demo technicians matching technicians.html.
2. services.csv: 7 service categories currently shown in the project.
3. emergency_services.csv: 7 emergency options shown in the Emergency Services section.

Important:
- These are sample/demo records, not verified real technicians, ratings, prices, distances, availability or credentials.
- Contact fields are blank; add only verified contact details with permission.
- All records use Gorakhpur as the demo city, as confirmed.
- technicians.html currently has hardcoded cards. Updating technicians.csv alone will NOT automatically update those cards until the Flask route/template is connected to loop through the CSV.
- Check the actual Flask route and expected column names before replacing your existing technicians.csv.
- This emergency CSV lists options only; it does not save emergency bookings.
