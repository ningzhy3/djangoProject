from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from customer_portal.models import *
from django.contrib.auth.decorators import login_required
# from car_dealer_portal.models import *
from django.http import HttpResponseRedirect
import datetime
# Create your views here.
from django.shortcuts import redirect

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'customer/login.html')
    else:
        return render(request, 'customer/home_page.html')

def login(request):
    return render(request, 'customer/login.html')

def auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'customer/home_page.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        try:
            customer = Customer.objects.get(user = user)
        except:
            customer = None
        if customer is not None:
            auth.login(request, user)
            if user.is_superuser: 
                return redirect('customer/admin/')

            else :
                return render(request, 'customer/home_page.html')
        else:
            return render(request, 'customer/login_failed.html')

def logout_view(request):
    auth.logout(request)
    return render(request, 'customer/login.html')

def register(request):
    return render(request, 'customer/register.html')

def registration(request):
    username = request.POST['username']
    password = request.POST['password']
    
    firstname = request.POST['first_name']
    lastname = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    city = request.POST['city']
    city = city.lower()
    state = request.POST['state']
    zipcode = request.POST['zipcode']
    street = request.POST['street']
    customertype = request.POST['customer_type']

    dln = request.POST['dln']
    ins_name = request.POST['ins_name']
    ins_no = request.POST['ins_no']
    try:
        user = User.objects.create_user(username = username, password = password, email = email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'customer/registration_error.html')
    # try:
    #     area = Area.objects.get(city = city, pincode = pincode)
    # except:
    #     area = None
    # if area is not None:
    #     customer = Customer(user = user, mobile = mobile, area = area)
    # else:
    #     area = Area(city = city, pincode = pincode)
    #     area.save()
    #     area = Area.objects.get(city = city, pincode = pincode)

    customer = Customer(user = user, first_name = firstname, last_name = lastname, email = email, phone = phone,
    city = city, state = state, zipcode = zipcode, street = street, customer_type = customertype)

    coupon = Coupon.objects.get(id=1)

    customer.save()

    individual = Individual(user = user, first_name = firstname, last_name = lastname, email = email, phone = phone,
    city = city, state = state, zipcode = zipcode, street = street, customer_type = customertype, customer_ptr = customer, dln = dln, ins_name = ins_name, ins_no = ins_no,coupon = coupon)

    individual.save()
    return render(request, 'customer/registered.html')

# @login_required
# def search(request):
#     return render(request, 'customer/search.html')

# @login_required
# def search_results(request):
#     city = request.POST['city']
#     city = city.lower()
#     vehicles_list = []
#     area = Area.objects.filter(city = city)
#     for a in area:
#         vehicles = Vehicles.objects.filter(area = a)
#         for car in vehicles:
#             if car.is_available == True:
#                 vehicle_dictionary = {'name':car.car_name, 'color':car.color, 'id':car.id, 'pincode':car.area.pincode, 'capacity':car.capacity, 'description':car.description}
#                 vehicles_list.append(vehicle_dictionary)
#     request.session['vehicles_list'] = vehicles_list
#     return render(request, 'customer/search_results.html')


@login_required
def rent_vehicle(request):
    # # return render(request, 'customer/confirmation.html', )
    # return render(request, 'customer/rent_failed.html', )
    customer = Customer.objects.get(user = request.user)
    try: 
        rental_service = Rental_service.objects.get(customer_id = customer)
        vehicle = rental_service.vin
        vehicle_class = Vehicle_class.objects.get(id = vehicle.vehicle_class_id)
        # return render(request, 'customer/rent_failed.html', {'rental_service':rental_service}, {'vehicle_class':vehicle_class})
        return render(request, 'customer/rent_failed.html', {'rental_service':rental_service, 'vehicle_class':vehicle_class})
    except:
        # return render(request, 'customer/confirmation.html', )
        return render(request, 'customer/location.html', )


@login_required
def return_vehicle(request):
    
    customer = Customer.objects.get(user = request.user)
    try:
        rental_service = Rental_service.objects.get(customer_id = customer)
        try:
            invoice = Invoice.objects.get(rental_service = rental_service)
            return render(request, 'customer/return_failed.html')
        except:
            return render(request, 'customer/return.html', {'rental_service':rental_service})
    except:
        return render(request, 'customer/return_failed.html')

@login_required
def return_detail(request):
    customer = Customer.objects.get(user = request.user)

    rental_service = Rental_service.objects.get(customer_id = customer) 
    e_odometer = request.POST['e_odometer']
    #update rental_service table
    Rental_service.objects.filter(id=rental_service.id).update(e_odometer=e_odometer)
  
    vehicle = rental_service.vin
    vehicle_class = Vehicle_class.objects.get(id = vehicle.vehicle_class_id)

    rent_charge = vehicle_class.rent_charge
    extra_charge = vehicle_class.extra_charge

    s_odometer = rental_service.s_odometer
    e_odometer = rental_service.e_odometer
    d_odometer_limit = rental_service.d_odometer_limit

    if customer.customer_type == 'I':
        individual = Individual.objects.get(user = request.user)
        coupon = Coupon.objects.get(id = individual.coupon_id)
        discount = coupon.coupon_rate
    else:
        corporate = Corporate.objects.get(user = request.user)
        corporation = Corporation.objects.get(id = corporate.corporation)
        discount = corporation.corp_discount

    # interval = rental_service.d_date - rental_service.p_date
    interval = rental_service.d_date - rental_service.p_date
    days = interval.days

    if (e_odometer-s_odometer) > d_odometer_limit:
        sum = days*rent_charge + extra_charge*(e_odometer-s_odometer)
    else:
        sum = days*rent_charge

    amount=discount*sum
    # Rental_service.objects.filter(customer_id=customer).delete()
    date=datetime.date.today()

    invoice = Invoice(invoice_amount = amount, invoice_date = date, rental_service = rental_service)
    invoice.save()

    return render(request, 'customer/return_detail.html',)

    

@login_required
def invoice(request):
    customer = Customer.objects.get(user = request.user)
    try:
        rental_service = Rental_service.objects.get(customer_id = customer) 
        try:
            invoice = Invoice.objects.get(rental_service = rental_service)
            return render(request, 'customer/invoice.html',{'rental_service':rental_service, 'invoice':invoice})
        except:
            print(1)
            return render(request, 'customer/invoice_failed.html')
    except:
            print(2)
            return render(request, 'customer/invoice_failed.html')        

@login_required
def invoice_failed(request):
    return render(request, 'customer/invoice_failed.html') 
    

@login_required
def pay(request):
    customer = Customer.objects.get(user = request.user)
    rental_service = Rental_service.objects.get(customer_id = customer)
    invoice = Invoice.objects.get(rental_service = rental_service)
    return render(request, 'customer/pay.html',{'invoice':invoice})
    

@login_required
def confirm(request):
    username = request.user
    customer = Customer.objects.get(user = request.user)
    customer_id = customer.id 

    # days = request.POST['days']
    p_location = Location.objects.get(street_address = request.POST['p_location'])
    d_location = Location.objects.get(street_address = request.POST['d_location'])

    p_date = request.POST['p_date']
    d_date = request.POST['d_date']

    s_odometer = 20000
    e_odometer = 0
    d_odometer_limit = 100
    
    # vehicle = Vehicle.objects.get(model = request.POST['model'])
    vehicle = Vehicle.objects.get(model = request.POST['model'],location_id = p_location.id)

    rental_service = Rental_service(customer_id = customer, p_location = p_location,
    d_location = d_location, p_date = p_date, d_date = d_date, s_odometer = s_odometer,
    e_odometer = e_odometer, vin = vehicle, d_odometer_limit = d_odometer_limit)

    rental_service.save()
    vehicle = rental_service.vin
    vehicle_class = Vehicle_class.objects.get(id = vehicle.vehicle_class_id)

    return render(request, 'customer/confirmed.html',{'rental_service':rental_service, 'vehicle_class':vehicle_class})

    # if vehicle.is_available:
    #     car_dealer = vehicle.dealer
    #     rent = (int(vehicle.capacity))*300*(int(days))
    #     car_dealer.wallet += rent
    #     car_dealer.save()
    #     try:
    #         order = Orders(vehicle = vehicle, car_dealer = car_dealer, user = user, rent=rent, days=days)
    #         order.save()
    #     except:
    #         order = Orders.objects.get(vehicle = vehicle, car_dealer = car_dealer, user = user, rent=rent, days=days)
    #     vehicle.is_available = False
    #     vehicle.save()
    #     return render(request, 'customer/confirmed.html', {'order':order})
    # else:
    #     return render(request, 'customer/order_failed.html')

# @login_required
# def manage(request):
#     order_list = []
#     user = User.objects.get(username = request.user)
#     try:
#         orders = Orders.objects.filter(user = user)
#     except:
#         orders = None
#     if orders is not None:
#         for o in orders:
#             if o.is_complete == False:
#                 order_dictionary = {'id':o.id,'rent':o.rent, 'vehicle':o.vehicle, 'days':o.days, 'car_dealer':o.car_dealer}
#                 order_list.append(order_dictionary)
#     return render(request, 'customer/manage.html', {'od':order_list})

# @login_required
# def update_order(request):
#     order_id = request.POST['id']
#     order = Orders.objects.get(id = order_id)
#     vehicle = order.vehicle
#     vehicle.is_available = True
#     vehicle.save()
#     car_dealer = order.car_dealer
#     car_dealer.wallet -= int(order.rent)
#     car_dealer.save()
#     order.delete()
#     cost_per_day = int(vehicle.capacity)*300
#     return render(request, 'customer/confirmation.html', {'vehicle':vehicle}, {'cost_per_day':cost_per_day})

# @login_required
# def delete_order(request):
#     order_id = request.POST['id']
#     order = Orders.objects.get(id = order_id)
#     car_dealer = order.car_dealer
#     car_dealer.wallet -= int(order.rent)
#     car_dealer.save()
#     vehicle = order.vehicle
#     vehicle.is_available = True
#     vehicle.save()
#     order.delete()
#     return HttpResponseRedirect('/customer_portal/manage/')


@login_required
def pay_confirmed(request):

    payment_number = request.POST.get('payment_number')
    payment_method = request.POST.get('payment_method')
    payment_name = request.POST.get('payment_name')
    customer = Customer.objects.get(user = request.user)
    rental_service = Rental_service.objects.get(customer_id = customer) 
    invoice = Invoice.objects.get(rental_service = rental_service)
    vehicle = rental_service.vin
    vehicle_class = Vehicle_class.objects.get(id = vehicle.vehicle_class_id)

    payment_amount = invoice.invoice_amount

    payment_date = datetime.date.today()
    payment = Payment(payment_amount = payment_amount, payment_number = payment_number, 
    payment_method = payment_method, inovice = invoice, payment_date = payment_date)
    payment.save()

    rental_history = Rental_History(
        amount = payment_amount,
        p_date = rental_service.p_date,
        d_date = rental_service.d_date,
        s_odometer = rental_service.s_odometer,
        e_odometer = rental_service.e_odometer,
        d_odometer_limit = rental_service.d_odometer_limit,
        p_location = rental_service.p_location,
        d_location = rental_service.d_location,
        vehicle_type=vehicle_class.vehicle_type,
        payment_method = payment_method,
        i_date = invoice.invoice_date,

        # vin = rental_service.vin,
        customer = rental_service.customer_id,
        # invoice = invoice
    )
    rental_history.save()


    Rental_service.objects.filter(customer_id=customer).delete()

    return render(request, 'customer/pay_confirm.html')

@login_required
def profile(request):
    customer = Customer.objects.get(user = request.user)
    individual = Individual.objects.get(customer_ptr = customer)
    coupon = Coupon.objects.get(id = individual.coupon_id)

    # return render(request, 'customer/profile.html',{'customer':customer},{'individual':individual})
    return render(request, 'customer/profile.html',{'individual':individual, 'coupon':coupon})

@login_required
def edit(request):
    customer = Customer.objects.get(user = request.user)
    individual = Individual.objects.get(customer_ptr = customer)
    # return render(request, 'customer/profile.html',{'customer':customer},{'individual':individual})

    return render(request, 'customer/edit.html',{'individual':individual})

@login_required
def update(request):
    customer = Customer.objects.get(user = request.user)
    individual = Individual.objects.get(customer_ptr = customer)

    # username = request.POST['username']
    # password = request.POST['password']
    
    firstname = request.POST['first_name']
    lastname = request.POST['last_name']
    phone = request.POST['phone']
    email = request.POST['email']
    city = request.POST['city']
    city = city.lower()
    state = request.POST['state']
    zipcode = request.POST['zipcode']
    street = request.POST['street']
    # customertype = request.POST['customer_type']

    dln = request.POST['dln']
    ins_name = request.POST['ins_name']
    ins_no = request.POST['ins_no']
    try:
        # user = User.objects.create_user(username = username, password = password, email = email)
        # Individual.objects.filter(id=individual.id).update(first_name = firstname, last_name = lastname, email = email, phone = phone,
        # city = city, state = state, zipcode = zipcode, street = street, customer_type = customertype, customer_ptr = customer, 
        # dln = dln, ins_name = ins_name, ins_no = ins_no)
        Individual.objects.filter(id=individual.id).update(first_name = firstname, last_name = lastname, email = email, phone = phone,
        city = city, state = state, zipcode = zipcode, street = street, customer_ptr = customer, 
        dln = dln, ins_name = ins_name, ins_no = ins_no)
        customer = Customer.objects.get(user = request.user)
        individual = Individual.objects.get(customer_ptr = customer)
        coupon = Coupon.objects.get(id = individual.coupon_id)
    except:
        return render(request, 'customer/profile.html')

    # return render(request, 'customer/profile.html',{'customer':customer},{'individual':individual})
    return render(request, 'customer/profile.html',{'individual':individual, 'coupon':coupon})


@login_required
def order_detailed(request):
    customer = Customer.objects.get(user = request.user)
    rental_history = Rental_History.objects.filter(customer_id=customer)
    if rental_history:
        return render(request, 'customer/order.html', {'rental_history':rental_history})
    else:
        return render(request, 'customer/order.html', {'error': 'No order found.'})

def corp(request):
    return render(request, 'customer/corp_register.html')

def corp_registration(request):
    username = request.POST['username']
    password = request.POST['password']
    
    firstname = request.POST['first_name']
    lastname = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    city = request.POST['city']
    city = city.lower()
    state = request.POST['state']
    zipcode = request.POST['zipcode']
    street = request.POST['street']
    customertype = request.POST['customer_type']

    dln = request.POST['dln']
    ins_name = request.POST['ins_name']
    ins_no = request.POST['ins_no']
    try:
        user = User.objects.create_user(username = username, password = password, email = email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'customer/registration_error.html')

    customer = Customer(user = user, first_name = firstname, last_name = lastname, email = email, phone = phone,
    city = city, state = state, zipcode = zipcode, street = street, customer_type = customertype)

    coupon = Coupon.objects.get(id=1)

    customer.save()

    individual = Individual(user = user, first_name = firstname, last_name = lastname, email = email, phone = phone,
    city = city, state = state, zipcode = zipcode, street = street, customer_type = customertype, customer_ptr = customer, dln = dln, ins_name = ins_name, ins_no = ins_no,coupon = coupon)

    individual.save()
    return render(request, 'customer/registered.html')

def location(request):
    username = request.user
    customer = Customer.objects.get(user = request.user)
    customer_id = customer.id
    p_location = Location.objects.get(street_address = request.POST['p_location'])
    if p_location:
        vehicle = Vehicle.objects.filter(location_id = p_location.id)
        return render(request, 'customer/confirmation.html', {'p_location':p_location, 'vehicle':vehicle})
    else:
        return render(request, 'customer/confirmation.html', {'error': 'No order found.'})