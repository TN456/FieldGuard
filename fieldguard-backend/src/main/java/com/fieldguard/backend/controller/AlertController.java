package com.fieldguard.backend.controller;

import com.fieldguard.backend.model.Alert;
import com.fieldguard.backend.repository.AlertRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/alerts")
@CrossOrigin(origins = "*")
public class AlertController {

    private final AlertRepository alertRepository;

    public AlertController(AlertRepository alertRepository) {
        this.alertRepository = alertRepository;
    }

    @GetMapping("/severity/{level}")
    public List<Alert> findBySeverity(@PathVariable String level) {
        return alertRepository.findBySeverity(level);
    }

    @GetMapping
    public List<Alert> getAllAlerts(){
        return alertRepository.findAll();
    }
}
