import multiprocessing

def run_final():
    import final  # Run final.py

def run_sensor_motor():
    import sensors_motor  # Run sensor_motor.py

if __name__ == "__main__":
    # Create processes for final.py and sensor_motor.py
    process_final = multiprocessing.Process(target=run_final)
    process_sensor_motor = multiprocessing.Process(target=run_sensor_motor)

    # Start both processes
    process_final.start()
    process_sensor_motor.start()

    # Wait for both processes to finish
    process_final.join()
    process_sensor_motor.join()
ln
