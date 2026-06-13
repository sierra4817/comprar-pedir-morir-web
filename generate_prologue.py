import asyncio
import edge_tts
import os
import re
import subprocess

# Text to generate
text = """PRÓLOGO. Dos hombres, el mismo café.

Carlos tiene cuarenta y cinco años. Lleva veinte trabajando en una empresa de logística en las afueras de Madrid. Cobra treinta y ocho mil euros al año brutos, aunque en su cuenta nunca llegan tantos. Paga su hipoteca, educa a sus dos hijos, ahorra lo que puede y cada diciembre espera que la declaración de la renta no le salga a pagar.

Rodrigo también tiene cuarenta y cinco años. Nunca ha cobrado una nómina. Vive en un ático en el barrio de Sarriá, en Barcelona, viaja cuatro veces al año y tiene una cartera de inversiones valorada en doce millones de euros. Este año ha pagado en impuestos sobre la renta, exactamente, cero euros.

Ambos desayunan en cafeterías similares. Ambos leen las noticias por el móvil. Ambos se quejan del precio de la gasolina. Ambos son ciudadanos del mismo país, sujetos a las mismas leyes.

La diferencia no es la inteligencia. Tampoco el esfuerzo. Rodrigo no trabaja el doble que Carlos, ni es más listo, ni tiene más horas en el día. La diferencia es que cada uno está jugando a un juego distinto. Y lo más inquietante es que Carlos ni siquiera sabe que existen dos juegos.

"No es que los ricos eviten los impuestos. Es que el sistema nunca intentó alcanzarlos." — Albert Sierra.

Este libro nació de una pregunta incómoda que me hice hace años, sentado frente a un cliente cuyo patrimonio crecía a un ritmo que jamás yo habría imaginado posible: ¿por qué nadie enseña esto en las escuelas?

La respuesta, descubrí con el tiempo, es sencilla y perturbadora a la vez: porque el sistema no tiene ningún incentivo para hacerlo. Las reglas fiscales que permiten a los grandes patrimonios diferir, minimizar y, en última instancia, eludir el pago de impuestos no son errores del sistema. Son el sistema.

Lo que encontrarás en estas páginas no es una guía para evadir impuestos, ni un manual de paraísos fiscales, ni ningún truco ilegal. Es algo más poderoso: la descripción clara, honesta y accesible del mecanismo que separa a quienes acumulan riqueza de quienes trabajan toda su vida sin avanzar.

Tres verbos. Tres pasos. Una estrategia que los grandes patrimonios llevan décadas utilizando en silencio:"""

# Words with pauses
words = ["Comprar.", "Pedir prestado.", "Morir."]

# Ending text
ending = """Es hora de que conozcas el otro juego.

—Albert Sierra, Ginebra, Suiza."""

# Voice
voice = "es-ES-AlvaroNeural"

async def main():
    # Directories to write to
    destinations = [
        r"C:\Users\as\Desktop\01_Prologo.mp3",
        r"C:\Users\as\Desktop\AUDIOLIBROS_NUEVO\Comprar Pedir Prestado Morir\01_Prologo.mp3",
        r"C:\Users\as\Desktop\Audiolibros_y_Textos\Comprar Pedir Prestado Morir\01_Prologo.mp3",
        r"C:\Users\as\Downloads\Organizado\02_Proyecto_Libro_y_Ebooks\Audiolibro_y_Texto\01_Prologo.mp3"
    ]

    temp_files = []
    
    # We will split text into parts:
    # Part 0: Header and Intro text
    # Pause
    # Part 1: Carlos & Rodrigo details until colon
    # Pause
    # Part 2: "Comprar."
    # Pause
    # Part 3: "Pedir prestado."
    # Pause
    # Part 4: "Morir."
    # Pause
    # Part 5: Ending text

    parts = [
        "PRÓLOGO. Dos hombres, el mismo café.",
        text.replace("PRÓLOGO. Dos hombres, el mismo café.", "").strip(),
        "Comprar.",
        "Pedir prestado.",
        "Morir.",
        ending
    ]

    print("Generating parts via edge-tts...")
    for i, part in enumerate(parts):
        temp_path = f"temp_part_{i}.mp3"
        temp_files.append(temp_path)
        print(f"Generating {temp_path} for text: '{part[:40]}...'")
        communicate = edge_tts.Communicate(part, voice)
        await communicate.save(temp_path)

    # Generate silence file (1.5 seconds)
    silence_file = "temp_silence.mp3"
    print("Generating silence file...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", 
        "-t", "1.5", "-c:a", "libmp3lame", "-b:a", "48k", silence_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_files.append(silence_file)

    # We want to concatenate:
    # part_0 + silence + part_1 + silence + part_2 + silence + part_3 + silence + part_4 + silence + part_5
    concat_list = [
        "temp_part_0.mp3",
        silence_file,
        "temp_part_1.mp3",
        silence_file,
        "temp_part_2.mp3",
        silence_file,
        "temp_part_3.mp3",
        silence_file,
        "temp_part_4.mp3",
        silence_file,
        "temp_part_5.mp3"
    ]

    # Create list file for ffmpeg concat
    list_file_path = "concat_list.txt"
    with open(list_file_path, "w", encoding="utf-8") as f:
        for f_name in concat_list:
            # Escape single quotes and write
            f.write(f"file '{f_name}'\n")

    # Concatenate using ffmpeg concat demuxer
    output_temp = "output_merged.mp3"
    print("Concatenating parts using ffmpeg...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file_path, 
        "-c", "copy", output_temp
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Re-mux to clean up timelines and headers
    output_final_temp = "output_final.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-i", output_temp, "-c", "copy", output_final_temp
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Copy to all destinations
    for dest in destinations:
        dest_dir = os.path.dirname(dest)
        if os.path.exists(dest_dir):
            print(f"Saving to {dest}...")
            # Use binary copy
            with open(output_final_temp, "rb") as f_src:
                data = f_src.read()
            with open(dest, "wb") as f_dst:
                f_dst.write(data)
        else:
            print(f"Destination directory does not exist: {dest_dir}")

    # Cleanup temp files
    print("Cleaning up temporary files...")
    all_temp = temp_files + [list_file_path, output_temp, output_final_temp]
    # Remove files that starts with temp_part_
    for i in range(len(parts)):
        f_name = f"temp_part_{i}.mp3"
        if os.path.exists(f_name):
            os.remove(f_name)
    if os.path.exists(silence_file):
        os.remove(silence_file)
    if os.path.exists(list_file_path):
        os.remove(list_file_path)
    if os.path.exists(output_temp):
        os.remove(output_temp)
    if os.path.exists(output_final_temp):
        os.remove(output_final_temp)

    print("Done!")

if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
