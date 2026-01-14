package com.fieldguard.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fieldguard.backend.model.Alert;
import com.fieldguard.backend.repository.AlertRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class KafkaConsumerService {

    private final AlertRepository alertRepository;
    private final ObjectMapper objectMapper;

    public KafkaConsumerService(AlertRepository alertRepository, ObjectMapper objectMapper) {
        this.alertRepository = alertRepository;
        this.objectMapper = objectMapper;
    }

    @KafkaListener(topics = "animal-health-stream", groupId = "fieldguard-backend-group")
    public void consume(String message){
        try{
            JsonNode json = objectMapper.readTree(message);
            if(json.has("metrics")){
                JsonNode metrics = json.get("metrics");
                double temp = metrics.get("temperature").asDouble();
                int animalId = json.get("animal_id").asInt();

                if(temp > 40.0){
                    System.out.println("HIGH TEMPERATURE DETECTED: Animal " + animalId);
                    saveAlert(animalId, temp, metrics);
                }
            }
        }
        catch (Exception e){
            System.err.println("Error while consuming message: " + e.getMessage());
        }
    }

    private void saveAlert(int animalId, double temp, JsonNode metrics) {
        Alert alert = new Alert();
        alert.setAnimalId(animalId);
        alert.setSeverity("CRITICAL");
        alert.setDescription("Fever detected: " + temp + "°C");
        alert.setTimestamp(LocalDateTime.now());

        alert.setTemperature(temp);
        alert.setHeartRate(metrics.get("heart_rate").asDouble());
        alert.setRuminationIndex((metrics.get("rumination_index").asDouble()));

        alertRepository.save(alert);
        System.out.println("Alert saved to MongoDB for Animal #" + animalId);
    }
}
