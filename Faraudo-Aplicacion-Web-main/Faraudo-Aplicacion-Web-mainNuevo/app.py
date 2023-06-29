from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
from passver import PasswordVer

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Curso, Estudiante, Padre, Preceptor

def obtener_curso(id_curso):
    curso = Curso.query.get(id_curso)
    return curso

def obtener_cursos_asignados(id_preceptor):
    preceptor = Preceptor.query.get(id_preceptor)
    cursos_asignados = preceptor.cursos
    return cursos_asignados

def obtener_estudiantes_curso(id_curso):
    estudiantes = Estudiante.query.filter_by(idcurso=id_curso).order_by(Estudiante.apellido, Estudiante.nombre).all()
    return estudiantes


@app.route('/',) #PAGINA DE INICIO
def usuario():
    return render_template('login.html')

@app.route('/bienvenida', methods = ['POST', 'GET']) #LOGIN
def bienvenida():
    if request.method == "POST":
        if request.form['mail'] and request.form['contra'] and request.form['tipo']:
            if request.form['tipo'] == 'padre': #EVALUA EL TIPO, SI ES TIPO PADRE:
                padre = Padre.query.filter_by(correo=request.form['mail']).first() #FILTRA EN LA BASE DE DATOS CON EL MAIL Y OBTIENE EL PADRE
                if(padre is not None): #SI EXISTE LA CUENTA:
                    passver = PasswordVer(request.form['contra']) #VERIFICAMOS LA CONTRASE;A CON EL CIFRADO
                    if(passver.validarPassword(padre.clave)): #SI ES CORRECTA, GUARDAMOS LA SESSION Y ENTRAMOS AL CAMPUS
                        session["id"] = padre.id
                        session["mail"] = padre.correo
                        session["tipo"] = request.form['tipo']
                        return render_template('menupadre.html', datos=[padre.nombre, padre.apellido, session["tipo"]])
                flash('Verifica tus credenciales de acceso, Email o contraseña inválidos') #SI NO SALTA UN FLASH INDICANDO EL ERROR
                return render_template('login.html')
            else: #SI NO ES TIPO PADRE, ENTONCES SERA TIPO PRECEPTOR
                preceptor = Preceptor.query.filter_by(correo=request.form['mail']).first() #FILTRA EN LA BASE DE DATOS CON EL MAIL Y OBTIENE EL PRECEPTOR
                if(type(preceptor) is not None): #SI EXISTE LA CUENTA
                    passver = PasswordVer(request.form['contra'])
                    if(passver.validarPassword(preceptor.clave)):
                        session['preceptor_id'] = preceptor.id
                        session["mail"] = preceptor.correo
                        session["tipo"] = request.form['tipo']
                        return render_template('menupreceptor.html', datos=[preceptor.nombre,preceptor.apellido])
                flash('Verifica tus credenciales de acceso, Email o contraseña inválidos')
                return render_template('login.html')
        else:
            flash('Verifica tus credenciales de acceso, DNI o contraseña inválidos')
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout') #SE CIERRA LA SESION
def logout():
    session.pop('preceptor_id')
    session.pop('mail')
    session.pop('tipo')
    return redirect(url_for('usuario'))
@app.route('/informeprece')
def informeprece():
    preceptor = Preceptor.query.filter_by(id=session["preceptor_id"]).first()
    return render_template('informeprece.html', cursos=preceptor.cursos, r=range(len(preceptor.cursos)))


@app.route('/consinformeprece', methods=["GET", "POST"])
def consinformeprece():
    if request.method == "POST":
        curso_id = request.form.get('cursoid')
        if curso_id:
            curso = Curso.query.filter_by(id=curso_id).first()
            if curso:
                estudiantes = curso.estudiante
                informe = []

                for estudiante in estudiantes:
                    asistencias_aula = 0
                    asistencias_fisica = 0
                    inasistencias_aula_justificadas = 0
                    inasistencias_aula_injustificadas = 0
                    inasistencias_fisica_justificadas = 0
                    inasistencias_fisica_injustificadas = 0
                    total_inasistencias = 0
                    
                
                    for asistencia in estudiante.asistencia_alum:
                        if asistencia.codigoclase == 1:
                            if asistencia.asistio == "s":
                                asistencias_aula += 1
                            else:
                                if asistencia.asistio == "n":
                                    if asistencia.justificacion is not None:
                                        inasistencias_aula_justificadas += 1
                                    else:
                                        inasistencias_aula_injustificadas += 1
                        else:
                            if asistencia.asistio == "s":
                                asistencias_fisica += 1
                            else:
                                if asistencia.asistio == "n":
                                    if asistencia.justificacion is not None:
                                        inasistencias_fisica_justificadas += 1
                                    else:
                                        inasistencias_fisica_injustificadas += 1
                                    
                    total_inasistencias = inasistencias_aula_injustificadas +  inasistencias_aula_justificadas + (inasistencias_fisica_justificadas + inasistencias_fisica_injustificadas) / 2

                    informe.append(
                        {
                            "estudiante": estudiante,
                            "asistencias_aula": asistencias_aula,
                            "asistencias_fisica": asistencias_fisica,
                            "inasistencias_aula_justificadas": inasistencias_aula_justificadas,
                            "inasistencias_aula_injustificadas": inasistencias_aula_injustificadas,
                            "inasistencias_fisica_justificadas": inasistencias_fisica_justificadas,
                            "inasistencias_fisica_injustificadas": inasistencias_fisica_injustificadas,
                            "total_inasistencias": total_inasistencias,
                        }
                    )

                return render_template("consinformeprece.html", curso=curso, informe=informe)

    return redirect(url_for('bienvenida'))

@app.route("/curso")
def curso():
    preceptor = Preceptor.query.filter_by(id=session["id"]).first()
    return render_template('curso.html', cursos=preceptor.cursos, r=range(len(preceptor.cursos)))


@app.route("/regasis", methods=["GET", "POST"])
def regasis():
    if request.method == "POST":
        if request.form['cursoid']:
            curso = Curso.query.filter_by(id=request.form['cursoid']).first()
            session["asis"] = curso.id
            return render_template('regasis.html', curso=curso, estudiantes=curso.estudiante, r=range(len(curso.estudiante)))
    else:
        return redirect(url_for('curso'))


@app.route('/asisreg', methods=['GET', 'POST'])
def asisreg():
    if request.method == "POST":
        curso = Curso.query.filter_by(id=session["asis"]).first()
        estudiantes = curso.estudiante
        for i in range(len(estudiantes)):
            codcl = request.form.get(f'tipo{i}', '')
            fech = request.form.get(f'fe{i}', '')
            asi = request.form.get(f'asis{i}', '')
            justi = request.form.get(f'justi{i}', '')
            asistencia = Asistencia(fecha=fech, codigoclase=int(codcl), asistio=asi, justificacion=justi, idestudiante=estudiantes[i].id)
            db.session.add(asistencia)
        db.session.commit()
        flash('Asistencia cargada')
        return redirect(url_for('regasis'))
    else:
        return redirect(url_for('regasiscurso'))

if __name__ == '__main__': 
    app.run(debug = True)