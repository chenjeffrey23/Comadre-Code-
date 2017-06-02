from flask import Flask, render_template, flash, request
from marketing_notifications_python.forms import SendMessageForm
from marketing_notifications_python.models import init_models_module
from marketing_notifications_python.twilio import init_twilio_module
from marketing_notifications_python.view_helpers import twiml, view
from flask import Blueprint
from marketing_notifications_python.twilio.twilio_services import TwilioServices

# WHEN ADDING SPANISH CHARACTERS I GET in _escape_cdata
#     return text.encode(encoding, "xmlcharrefreplace")
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 218: ordinal not in range(128)
# even with encoding=utf8 at the top of this file

def construct_view_blueprint(app, db):
    SUBSCRIBE_COMMAND = "subscribe"
    UNSUBSCRIBE_COMMAND = "finished"
    SUBSCRIBE_COMMAND_SPANISH = "inscribe"
    UNSUBSCRIBE_COMMAND_SPANISH = "alto"

    views = Blueprint("views", __name__)

    init_twilio_module(app)
    init_models_module(db)
    from marketing_notifications_python.models.subscriber import Subscriber

    @views.route('/', methods=["GET", "POST"])
    @views.route('/notifications', methods=["GET", "POST"])
    def notifications():
        form = SendMessageForm()
        if request.method == 'POST' and form.validate():
            flash(form.language.data)
            flash(form.zipCode.data)
            for zip in form.zipCode.data:
                flash(zip.strip('u'))
            flash(form.interest.data)
            for i in form.interest.data:
                flash(i.strip('u'))
            flash(form.childAge.data)
            temp1= set()
            subscribers=[]
            flash(form.message.data)
            for zips in form.zipCode.data:
                if zips != "All":
                    tempzip=int(zips)
                    temp1.update(Subscriber.query.filter(Subscriber.zipcode == tempzip).all())
                else:
                    temp1.update(Subscriber.query.filter(Subscriber.subscribed).all())
            if (form.language.data)== "Spanish":
                temp1.intersection_update(Subscriber.query.filter(Subscriber.spanish).all())
            for i in (form.interest.data):
                if i == "All":
                    temp1.intersection_update(Subscriber.query.filter(Subscriber.interests == 4).all())
                elif i == "Science/Tech":
                    temp1.intersection_update(Subscriber.query.filter(Subscriber.interests == 1).all())
                elif i == "Arts":
                    temp1.intersection_update(Subscriber.query.filter(Subscriber.interests == 2).all())
                else:
                    temp1.intersection_update(Subscriber.query.filter(Subscriber.interests == 3).all())
            if form.childAge.data != "":
                ages = (form.childAge.data.split(" "))
                for age in ages:
                    if len(temp1)>0:
                        for subs in temp1:
                            subages = subs.age.split(" ")
                            for subage in subages:
                                if subage == age:
                                    subscribers.append(subs)
            else:
                subscribers = temp1

            #temp2 = Subscriber.query.filter(Subscriber.age == form.childAge.data).all()
            #stemp2 = set(temp2)

            #subscribers= Subscriber.query.filter(Subscriber.subscribed).all()
            if len(subscribers) > 0:
                flash('Messages on their way!')
                twilio_services = TwilioServices()
                for s in subscribers:
                    twilio_services.send_message(s.phone_number, form.message.data)
            else:
                flash('No subscribers found!')

            form.reset()
            return view('notifications', form)

        return render_template('notifications.html', form=form)

    @views.route('/message', methods=["POST"])
    def message():
        subscriber = Subscriber.query.filter(Subscriber.phone_number == request.form['From']).first()
        if subscriber is None:
            subscriber = Subscriber(phone_number=request.form['From'])
            db.session.add(subscriber)
            db.session.commit()
            output = "Thanks for contacting the UCI parent text message study. Text " \
                     "\"subscribe\" if you would like to receive updates via text message in English. " \
                     "Texto \"inscribe\" si desea recibir actualizaciones por mensaje de texto en espanol."

        elif not subscriber.subscribed:
            output = _process_message(request.form['Body'], subscriber)
            db.session.commit()

        elif subscriber.zipcode is None and subscriber.spanish:
            output = _process_zip_spanish(request.form['Body'], subscriber)
            db.session.commit()

        elif subscriber.zipcode is None and not subscriber.spanish:
            output = _process_zip(request.form['Body'], subscriber)
            db.session.commit()
        
        elif subscriber.age is None and subscriber.spanish:
            output = _process_age_spanish(request.form['Body'], subscriber)
            db.session.commit()

        elif subscriber.age is None and not subscriber.spanish:
            output = _process_age(request.form['Body'], subscriber)
            db.session.commit()

        elif subscriber.interests is None and subscriber.spanish:
            output =  _process_interests_spanish(request.form['Body'], subscriber)
            db.session.commit()

        elif subscriber.interests is None and not subscriber.spanish:
            output = _process_interests(request.form['Body'], subscriber)
            db.session.commit()

        else:  # trying to fix the unbound local error message that happens after trying to unsubscribe after signup,
                # this fixes it
            output = _process_message(request.form['Body'], subscriber)
            db.session.commit()

        twilio_services = TwilioServices()
        return twiml(twilio_services.respond_message(output))

    def _process_message(message, subscriber):
        output = "Sorry, we don't recognize that command. Available commands are: \"subscribe\" or \"finished\". " \
                 "Lo sentimos, no reconocemos ese comando. Los comandos disponibles son: \"inscribe\" o \"alto\"."

        if message.lower().startswith(SUBSCRIBE_COMMAND) or message.lower().startswith(UNSUBSCRIBE_COMMAND):
            subscriber.subscribed = message.lower().startswith(SUBSCRIBE_COMMAND)
            subscriber.spanish = False;
            
            if subscriber.subscribed:
                output = "Thanks for signing up for the parent text message service. Please reply with your ZIP code."
            else:
                output = "You have unsubscribed from notifications and your data has been deleted."
                Subscriber.query.filter(Subscriber.phone_number == subscriber.phone_number).delete()

        elif message.lower().startswith(SUBSCRIBE_COMMAND_SPANISH) or message.lower().startswith(UNSUBSCRIBE_COMMAND_SPANISH):
            subscriber.subscribed = message.lower().startswith(SUBSCRIBE_COMMAND_SPANISH)
            subscriber.spanish = True;

            if subscriber.subscribed:
                output = "Gracias por inscribe para recibir mensajes de texto para padres! Porfavor responda con " \
                         "su codigo postal (ZIP)."
            else:
                output = "Has cancelado la suscripcion a las notificaciones."
                Subscriber.query.filter(Subscriber.phone_number == subscriber.phone_number).delete()

        return output

    def _process_zip_spanish(message, subscriber):

        output = "Lo sentimos, no reconocemos su codigo postal (ZIP). Porfavor vuelve a ingresar " \
                 "su codingo postal (ZIP)."

        if message[0].isdigit and len(message) == 5:
            subscriber.zipcode = message
            output = "Gracias! Porfavor responda con las edad(es) de su/s hijo/a. Separe las edades con un espacio."

        return output


    def _process_zip(message, subscriber):
        output = "Sorry, that's an invalid zipcode. Please reenter your zipcode."

        if message[0].isdigit() and len(message) == 5:
            subscriber.zipcode = message
            output = "Thanks! Please reply with the age(s) of your child. Separate multiple ages with a space."

        return output

    def _process_age_spanish(message, subscriber):
        ageList = message.strip(" ").split(" ")
        for age in ageList:
            if 0 > age > 18:
                output = "Lo sentimos, no reconocemos las edad(es) de su/s hijo/a. Porfavor vuelve a ingresar las " \
                         "edad(es) de su/s hijo/a. "
                return output
        subscriber.age = message
        output = "Gracias Porfavor responda con las areas que les interesan a su/s hijo/a: 1 ciencia / tecnologia, " \
                 "2 arte, 3 deportes, 4 todas estas areas!"
        return output

    def _process_age(message, subscriber):
        ageList = message.strip(" ").split(" ")
        for age in ageList:
            if 0 > age > 18:
                output = "Sorry, that's an invalid age. Please reenter your child's age."
                return output
        subscriber.age = message
        output = "Thanks! Please reply with your child's interests: 1 for science/tech, 2 for arts, " \
                 "3 for sports, 4 for all."
        return output

    def _process_interests_spanish(message, subscriber):
        output = "Lo sentimos, no reconocemos las areas que les interesan a su/s hijo/a. Porfavor vuelve a ingresar " \
                 "responda con las areas que les interesan a su/s hijo/a."

        if 0 < int(message) <= 4:
            subscriber.interests = message
            output = "Felicidades, ya se inscribio! Recibira mensajes semanales con avisos de actividades " \
                     "educativas/enriquecedoras y tambien con consejos para padres. Usted puede responder " \
                     "con \"alto\" cuando quiera poner fin a este servicio. Se aplican las tarifas estandar " \
                     "de mensajeria de texto y datos."

        return output

    def _process_interests(message, subscriber):
        output = "Sorry, that's an invalid interest. Please reenter your child's interests: 1 for science/tech, " \
                 "2 for arts, 3 for sports, 4 for all."

        if 0 < int(message) <= 4:
            subscriber.interests = message
            output = "You're all set. You'll get info a few times per week on out of school learning opportunities " \
                     "and advice. Reply \"finished\" at any time to stop these messages and delete your data. " \
                     "Standard text messaging and data rates apply."

        return output

    return views
