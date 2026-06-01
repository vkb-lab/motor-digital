from k_atlas.autonomous_executor import create_job_from_command, run_autonomous_command

def test_job_created_from_command():
    job = create_job_from_command("Crie campanha para Parada Atlantida")
    assert job["client_id"] == "parada_atlantida"
    assert len(job["tasks"]) >= 5

def test_autonomous_command_final_status():
    result = run_autonomous_command("Crie uma campanha para Parada Atlantida com landing page, QR Code, post Instagram, criativo visual e fila de publicacao.")
    assert result["status"] == "PENDING_FINAL_APPROVAL"
    assert result["external_call_executed"] is False
