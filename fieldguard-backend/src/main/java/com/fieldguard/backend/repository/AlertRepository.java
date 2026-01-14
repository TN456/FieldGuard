package com.fieldguard.backend.repository;

import com.fieldguard.backend.model.Alert;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AlertRepository extends MongoRepository<Alert,String> {

    // Find All Alerts for specific animal
    List<Alert> findByAnimalId(Integer animalId);

    // Find only critical alerts
    List<Alert> findBySeverity(String severity);
}
